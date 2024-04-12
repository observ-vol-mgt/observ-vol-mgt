from . import utils


class Signal:
    def __init__(self, type, metadata=None, time_series=None):
        self.type = type
        self.metadata = metadata
        self.time_series = time_series

    def set_time_series(self, time_series):
        if not utils.is_dataframe(time_series):
            raise Exception("Time series must be a pandas DataFrame")

        self.time_series = time_series

    def __str__(self):
        return f"Signal: type: {self.type}, metadata: {self.metadata}, time_series:{self.time_series}"
