from collections import OrderedDict
import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import ctypes

_hook = OrderedDict()


class _AppRunner(threading.Thread):
    def __init__(self, name, hook, **kwargs):
        threading.Thread.__init__(self, name=name, daemon=True)
        self.hook = hook
        self.kwargs = kwargs

    def run(self):
        app = dash.Dash(
            __name__,
            external_stylesheets=[
                'https://raw.githubusercontent.com/dmadisetti/KSPCommand/master/assets/styles.css '
            ])

        app.layout = html.Div([
            dcc.Tabs(id="tabs",
                     value='graphs',
                     children=[
                         dcc.Tab(label='Graphs', value='graphs'),
                         dcc.Tab(label='Orbits', value='world'),
                         dcc.Tab(label='Map', value='map'),
                     ]),
            html.Div(id="container"),
            dcc.Interval(
                id='interval-component',
                interval=1 * 1000,  # in milliseconds
                n_intervals=0)
        ])

        # Multiple components can update everytime interval gets fired.
        def update_graph_live():
            # Create the graph with subplots
            fig = plotly.subplots.make_subplots(rows=2,
                                                cols=1,
                                                vertical_spacing=0.2)
            fig['layout']['margin'] = {'l': 30, 'r': 10, 'b': 30, 't': 10}
            fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

            def subplot_generator():
                yield 1, 2

            for (_, dashboard) in hook.items():
                x, y = dashboard.step()
                row, col = subplot_generator()
                fig.append_trace(
                    {
                        'x': x,
                        'y': y,
                        'name': dashboard.name,
                        'text': dashboard.text,
                        'mode': 'lines+markers',
                        'type': 'scatter'
                    }, row, col)

                fig.update_layout(
                    title_text='Command Center',
                    xaxis=go.layout.XAxis(rangeselector=dict(buttons=list([
                        dict(count=10, label="now", stepmode="backward"),
                        dict(step="all")
                    ])),
                                          rangeslider=dict(visible=True)))

            return fig

        @app.callback(Output('container', 'children'), [Input('tab', 'value')])
        def display_content(selected_tab):
            if selected_tab == "world" or selected_tab == "map":
                return html.Div([
                    html.H1("KSPCommand World View"),
                    html.Iframe(
                        src=
                        "https://raw.githack.com/dmadisetti/KSPCommand/master/assets/index.html"
                    )
                ])
            return html.Div([
                html.H1("KSPCommand Graphs"),
                dcc.Graph(id='graph', figure=update_graph_live())
            ])

        app.callback(Output('live-update-graph', 'figure'),
                     events=[Event('interval-component', 'interval')],
                     state=[State('tab', 'value')])(update_graph_live)

        app.run_server(debug=True, dev_tools_hot_reload=False, **self.kwargs)

    def stop(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            thread_id, ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')


class _Dashboard(object):
    __slots__ = ["name", "text", "fn"]

    def __init__(self, fn, name, text):
        self.name = name
        self.text = text
        self.fn = fn
        self.steps = [self._extract_results()]

    def _extract_results(self):
        t0 = self.fn()
        if len(t0) != 2:
            raise KSPCommandException("Wrapped function must provide x and y")
        return t0

    def _step(self):
        self.steps.append(_extract_results())
        return zip(*self.steps)


def AppThread(name, **kwargs):
    return _AppRunner(name, _hook, **kwargs)


def graph(name="No Name", description=""):
    if name in _hook:
        raise KSPCommandException("Dash name has already been registered.")

    def wrapper(fn):
        d = Dashboard(fn, name, description)
        _hook[name] = d
        return fn

    return wrapper


def remove(name):
    if name not in _hook:
        raise KSPCommandException("Dash not registered.")
    del _hook[name]
