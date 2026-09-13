# =========================================================
# imports
# =========================================================

from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State

# =========================================================
# server
# =========================================================


class Server:
    """the Dash plumbing around a live figure"""

    def __init__(self, figure, title, interval_ms, on_update, reduce=None):
        """build the server around the figure and wire the update"""
        # dash
        self._dash = Dash(title)

        # layout
        self._dash.layout = html.Div(
            [
                dcc.Checklist(
                    id="reduce",
                    options=["downsample"] if reduce else [],
                    value=["downsample"] if reduce else [],
                ),
                dcc.Graph(
                    id="graph",
                    figure=figure,
                    style={"height": "95vh"},
                ),
                dcc.Interval(
                    id="interval",
                    interval=interval_ms,
                ),
            ]
        )

        # callback
        self._dash.callback(
            Output("graph", "figure"),
            Input("interval", "n_intervals"),
            State("reduce", "value"),
        )(on_update)

    def run(self):
        """start the Dash server"""
        self._dash.run()
