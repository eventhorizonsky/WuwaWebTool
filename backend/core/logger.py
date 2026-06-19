"""Minimal logger module replacing gsuid_core.logger."""
import logging
import sys

logger = logging.getLogger("wuwa_web")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(
    "[%(levelname)s] %(name)s: %(message)s"
))
logger.addHandler(handler)

# Save original methods BEFORE monkey-patching
_info = logger.info
_warning = logger.warning
_error = logger.error
_exception = logger.exception


def success(msg):
    _info(msg)


def warning(msg):
    _warning(msg)


def error(msg):
    _error(msg)


def exception(msg, *args, exc_info=True):
    _exception(msg, *args, exc_info=exc_info)


# Attach convenience aliases (using saved references, safe)
logger.success = success
logger.warning = warning
logger.error = error
logger.exception = exception
