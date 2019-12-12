import logging
import sys


class Logger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        handler = logging.StreamHandler(sys.stdout)
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(name)s:%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        self.addHandler(handler)

    def line_separator(self,):
        self.debug("========")
