# =========================================================
# imports
# =========================================================

from datetime import datetime, timedelta

import plotly.graph_objects as go
from dash import Patch

# =========================================================
# view
# =========================================================


class View:
    """the live figure and its per-tick patch"""

    def __init__(self, names, title, leading=None):
        """build the live figure, one trace per name"""
        self._names = names
        self._leading = leading
        self.figure = self._figure(title)

    # =========================================================
    # figure
    # =========================================================

    def _figure(self, title):
        """assemble the traces, the now-line and the layout"""
        figure = go.Figure()

        # traces
        for name in self._names:
            figure.add_trace(
                go.Scatter(
                    x=[],
                    y=[],
                    mode="lines",
                    name=name,
                )
            )

        # leading
        if self._leading:
            figure.add_shape(
                type="line",
                x0=datetime.now(),
                x1=datetime.now(),
                y0=0,
                y1=1,
                yref="paper",
                line={"dash": "dash", "color": "grey"},
                name=self._leading,
                showlegend=True,
            )

        # layout
        figure.update_layout(
            title=title,
            uirevision="hold",
            margin={"l": 40, "r": 20, "t": 50, "b": 40},
        )

        return figure

    # =========================================================
    # render
    # =========================================================

    def render(self, windows):
        """project each named window onto its trace as one patch"""
        patch = Patch()
        now = datetime.now()

        # traces
        self._render_traces(
            patch=patch,
            windows=windows,
        )

        # leading
        if self._leading:
            self._render_leading(
                patch=patch,
                now=now,
            )
            self._render_range(
                patch=patch,
                windows=windows,
                now=now,
            )

        return patch

    def _render_traces(self, patch, windows):
        """project a window's arrays onto its trace"""
        for index, name in enumerate(self._names):
            times, values = windows[name]

            # trace
            trace = patch["data"][index]
            trace["x"] = times
            trace["y"] = values

    def _render_leading(self, patch, now):
        """advance the leading line to now"""
        line = patch["layout"]["shapes"][0]
        line["x0"] = now
        line["x1"] = now

    def _render_range(self, patch, windows, now):
        """pin the view just past the now-line"""
        # starts
        starts = []
        for name in self._names:
            times, _values = windows[name]
            if len(times) > 0:
                starts.append(times[0])

        # guard
        if len(starts) == 0:
            return

        # pin
        span = (now - min(starts)).total_seconds()
        axis = patch["layout"]["xaxis"]
        axis["range"] = [
            min(starts),
            now + timedelta(seconds=max(3, span * 0.05)),
        ]
