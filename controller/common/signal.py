from common import utils


class Signal:
    def __init__(self, type, time_series=None):
        self.type = type
        self.time_series = time_series

    def set_time_series(self, time_series):
        if not utils.is_dataframe(time_series):
            raise Exception("Time series must be a pandas DataFrame")

        self.time_series = time_series

    def __str__(self):
        return f"Signal: type: {self.type}, time_series:{self.time_series}"
