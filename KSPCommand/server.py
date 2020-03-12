from collections import OrderedDict
import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import ctypes
from sympy import factorint
import threading
import sys

from .exception import KSPCommandException

_hook = OrderedDict()


def _split_int(i):
    if i < 4:
        return 1, i

    factors = sum([[
        k,
    ] * v for k, v in factorint(i).items()], [])
    if len(factors) == 1:
        return _split_int(i + 1)

    a = b = 1
    while len(factors) > 0:
        if min(a, b) == a:
            a *= factors.pop()
        else:
            b *= factors.pop()
        factors.reverse()
    return a, b


class _AppRunner(threading.Thread):
    def __init__(self, name, hook, **kwargs):
        threading.Thread.__init__(self, name=name, daemon=True)
        self.hook = hook
        self.kwargs = kwargs

    def run(self):
        app = dash.Dash(
            __name__,
            external_stylesheets=[
                'https://raw.githack.com/dmadisetti/KSPCommand/master/assets/styles.css'
            ])
        app.config['suppress_callback_exceptions'] = True

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
                interval=5 * 1000,  # in milliseconds
                n_intervals=0)
        ])

        # Multiple components can update everytime interval gets fired.
        def update_graph_live():
            # Create the graph with subplots
            rows, cols = _split_int(len(self.hook))
            fig = plotly.subplots.make_subplots(rows=rows,
                                                cols=cols,
                                                subplot_titles=tuple(
                                                    self.hook.keys()),
                                                vertical_spacing=0.2)
            fig['layout']['margin'] = {'l': 30, 'r': 10, 'b': 30, 't': 10}
            fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

            def subplot_generator(i):
                return 1 + i // cols, 1 + i % cols

            for (i, (title, dashboards)) in enumerate(self.hook.items()):
                row, col = subplot_generator(i)
                for dashboard in dashboards.values():
                    x, y = dashboard.step()
                    fig.append_trace(
                        {
                            'x': x,
                            'y': y,
                            'mode': 'lines+markers',
                            'type': 'scatter',
                            'name': dashboard.name,
                            'text': dashboard.text,
                        }, row, col)
            fig.update_layout(
                title_text='Command Center',
                **{
                    f"xaxis{i}": {
                        "autorange": True,
                        "rangeslider": {
                            "autorange": True,
                        },
                    }
                    for i in range(1,
                                   len(self.hook) + 1)
                },
            )
            return fig

        @app.callback(Output('container', 'children'),
                      [Input('tabs', 'value')])
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
                dcc.Graph(figure=update_graph_live(),
                          id='live-update-graph',
                          animate=True)
            ])

        @app.callback(Output('live-update-graph', 'figure'),
                      [Input('interval-component', 'n_intervals')])
        def heartbeat(n):
            result = update_graph_live()
            print(n, result, file=sys.stderr)
            return result

        app.run_server(debug=True,
                       dev_tools_props_check=True,
                       use_reloader=False,
                       **self.kwargs)

    def clear(self):
        for dashboards in self.hook.values():
            for dashboard in dashboards.values():
                if not dashboard.preset:
                    dashboard.steps = []

    def stop(self):
        thread_id = self.ident
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            thread_id, ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')


class _Dashboard(object):
    __slots__ = ["name", "text", "fn", "steps", "preset"]

    def __init__(self, fn, name, text, steps=None):
        self.name = name
        self.text = text
        self.fn = fn
        self.steps = steps
        self.preset = self.steps is not None
        if not self.preset:
            self.steps = [self._extract_results()]

    def _extract_results(self):
        t0 = self.fn()
        if len(t0) != 2:
            raise KSPCommandException("Wrapped function must provide x and y")
        return t0

    def step(self):
        if not self.preset:
            self.steps.append(self._extract_results())
        return zip(*self.steps)


def AppThread(name, **kwargs):
    return _AppRunner(name, _hook, **kwargs)


def remove(name):
    found = False
    for key in _hook:
        if name in _hook[key]:
            found = True
            del _hook[key][name]
    if name not in _hook and not found:
        raise KSPCommandException("Dash not registered.")
    else:
        del _hook[name]


def live_graph(key=None, name="No Name", description=""):
    if name in _hook:
        remove(name)

    if key is None:
        key = name

    def wrapper(fn):
        d = _Dashboard(fn, name, description)
        data = _hook.get(key, OrderedDict())
        data[name] = d
        _hook[key] = data
        return fn

    return wrapper


def graph(x, y, key=None, name="No Name", description=""):
    i = 0

    def fn():
        result = steps[i]
        i += 1
        i %= len(steps)
        return result

    steps = zip(x, y)
    d = _Dashboard(fn, name, description, steps=steps)
    data = _hook.get(key, {})
    data[name] = d
    _hook[key] = data
