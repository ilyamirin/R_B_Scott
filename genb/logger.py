import logging
import sys


class Logger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        handler = logging.StreamHandler(sys.stdout)
        self.addHandler(handler)

    def line_separator(self,):
        self.debug("========")
