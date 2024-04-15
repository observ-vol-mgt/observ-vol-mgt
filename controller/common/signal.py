from . import utils


class Signal:
    def __init__(self, type, metadata={}, time_series=None):
        self.type = type
        self.metadata = metadata
        self.time_series = time_series

    def set_time_series(self, time_series):
        if not utils.is_dataframe(time_series):
            raise Exception("Time series must be a pandas DataFrame")

        self.time_series = time_series

    def __str__(self):
        return f"Signal: type: {self.type}, metadata: {self.metadata}, time_series:{self.time_series}"


class Signals:
    def __init__(self, metadata={}, signals=None):
        if signals is None:
            signals = []
        self.metadata = metadata
        self.signals = signals

    def append(self, signal):
        self.signals.append(signal)

    def __iter__(self):
        return iter(self.signals)

    def __getitem__(self, index):
        if isinstance(index, int):
            if 0 <= index < len(self.signals):
                return self.signals[index]
            else:
                raise IndexError("Index out of range")
        elif isinstance(index, slice):
            return [self.signals[i] for i in range(*index.indices(len(self.signals)))]
        else:
            raise TypeError("Indices must be integers or slices")

    def __str__(self):
        return f"Signal: metadata: {self.metadata}, signals:{self.signals}"
