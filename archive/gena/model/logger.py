import logging
import sys

logger = logging.getLogger("genb")


def configure_logger():
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)