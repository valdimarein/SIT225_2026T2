# =========================================================
# imports
# =========================================================

import logging
from collections import deque
from datetime import datetime

log = logging.getLogger("memory")

# =========================================================
# memory
# =========================================================


class Memory:
    """a bounded window per named variable"""

    def __init__(self, names, window_points):
        """create one bounded window per name"""
        # windows
        self._windows = {}
        self._last = {}
        for name in names:
            self._windows[name] = deque(maxlen=window_points)

    def push(self, name, value, timestamp=None):
        """append one point to a window"""
        # stamp
        if timestamp is None:
            timestamp = datetime.now()

        # append
        self._windows[name].append((timestamp, value))

        # gap
        gap = 0.0
        if name in self._last:
            gap = (timestamp - self._last[name]).total_seconds()
        self._last[name] = timestamp

        log.info(f"{timestamp:%H:%M:%S} {name}: {value:.3f}  (+{gap:.2f}s)")

    def window(self, name):
        """return a window as parallel time and value lists"""
        # snapshot
        points = list(self._windows[name])

        # split
        times = []
        values = []
        for timestamp, value in points:
            times.append(timestamp)
            values.append(value)

        return times, values
