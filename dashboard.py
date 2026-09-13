# =========================================================
# imports
# =========================================================

from collections import defaultdict
from operator import itemgetter

from memory import Memory
from server import Server
from source import Source
from view import View

# =========================================================
# constants
# =========================================================

BIN_SECONDS = 5.0

SOURCES = {
    "arduino": Source,
}

SETTINGS = {
    "title": "live stream",
    "interval_ms": 250,
    "window_points": 300,
}

# =========================================================
# dashboard
# =========================================================


class Dashboard:
    """a live dashboard for any continuously pushed variable"""

    def __init__(self, source, methods=None, settings=None):
        """assemble the memory, the view and the server"""
        self._names = source["names"]
        self._source = source
        self._methods = methods or {}
        self._settings = SETTINGS | (settings or {})

        # reducer
        match self._methods.get("reduce", "minmax"):
            case "plain":
                self._reducer = self._plain
            case "mean":
                self._reducer = self._mean
            case "minmax":
                self._reducer = self._minmax

        # memory
        self._memory = Memory(
            names=self._names,
            window_points=self._settings["window_points"],
        )
        self.push = self._memory.push

        # view
        self._view = View(
            names=self._names,
            title=self._settings["title"],
            leading=self._methods.get("leading"),
        )

        # server
        self._server = Server(
            figure=self._view.figure,
            title=self._settings["title"],
            interval_ms=self._settings["interval_ms"],
            on_update=self._update,
            reduce=self._methods.get("reduce"),
        )

    # =========================================================
    # downsample
    # =========================================================

    def downsample(self, times, values, bin_seconds):
        """bin the window and reduce each bin by the chosen method"""
        # bin
        bins = self._bin(
            times=times,
            values=values,
            bin_seconds=bin_seconds,
        )

        # reduce
        out = self._reduce(bins)

        return out["times"], out["values"]

    def _bin(self, times, values, bin_seconds):
        """collect points into time bins"""
        bins = defaultdict(list)
        for timestamp, value in zip(times, values):
            # key
            epoch = timestamp.timestamp()
            key = int(epoch // bin_seconds)

            # collect
            bins[key].append((timestamp, value))

        return bins

    def _reduce(self, bins):
        """emit each bin's reduced points in occurrence order"""
        out = {
            "times": [],
            "values": [],
        }
        for key in sorted(bins):
            for timestamp, value in self._reducer(bins[key]):
                out["times"].append(timestamp)
                out["values"].append(value)

        return out

    # =========================================================
    # reducers
    # =========================================================

    def _plain(self, points):
        """keep the first point"""
        return [points[0]]

    def _mean(self, points):
        """average the values, stamped at the first timestamp"""
        total = 0.0
        for _timestamp, value in points:
            total += value
        return [(points[0][0], total / len(points))]

    def _minmax(self, points):
        """keep the lowest and highest, in time order"""
        low = min(points, key=itemgetter(1))
        high = max(points, key=itemgetter(1))
        return sorted({low, high})

    # =========================================================
    # update
    # =========================================================

    def _update(self, _n_intervals, reduce):
        """project every window onto the figure as one patch"""
        # windows
        windows = {}
        for name in self._names:
            times, values = self._memory.window(name)

            # downsample
            if reduce:
                times, values = self.downsample(
                    times=times,
                    values=values,
                    bin_seconds=BIN_SECONDS,
                )

            windows[name] = (times, values)

        return self._view.render(windows)

    # =========================================================
    # server
    # =========================================================

    def run(self):
        """connect the source and start the Dash server"""
        # connect
        kind = SOURCES[self._source["name"]]
        source = kind(
            push=self.push,
            names=self._names,
            thing_id=self._source["thing_id"],
            with_timestamps=self._methods.get("timestamps", False),
        )
        source.start()

        self._server.run()
