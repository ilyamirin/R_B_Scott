class Note:
    def __init__(self, instrument: int, start_time: float, end_time: (int, None) = None):
        self.start_time = start_time
        self.end_time = end_time
        self.instrument = instrument
