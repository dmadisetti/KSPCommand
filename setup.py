from setuptools import setup

# For any additional packages, please add them here.
REQS = [
    "futures==3.1.1",
    "yapf==0.24.0",
    "krpc==0.4.8",
    "dash.ly",
    "dash",
    "dash-html-components",
    "dash-core-components",
    "dash-table",
    "pyorbital",
]

setup(
    name='KSPCommand',
    version='0.0.1',
    packages=[
        'KSPCommand'
    ],
    url='https://github.com/dmadisetti/KSPCommand',
    tests_require=['nose'],
    include_package_data=True,
    license='MIT',
    author='Dylan Madisetti',
    author_email='contact@postmodern.technology',
    description=("TODO: Describe"),
    install_requires=REQS,
)
