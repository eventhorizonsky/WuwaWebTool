import logging
logger = logging.getLogger("gsuid_core")
logger.setLevel(logging.WARNING)
h = logging.StreamHandler()
h.setLevel(logging.WARNING)
logger.addHandler(h)
