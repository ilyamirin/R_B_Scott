class Note:
    def __init__(self, note: int, instrument: int, velocity: int, start_time: float, end_time: (int, None) = None):
        self.note = note
        self.instrument = instrument
        self.velocity = velocity
        self.start_time = start_time
        self.end_time = end_time

    @property
    def duration(self):
        return self.end_time - self.start_time
