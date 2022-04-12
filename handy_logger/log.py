# -*- coding: utf-8 -*-
import pprint
import logging

from .utils import get_caller_module_name, load_yaml_to_dict
from .decorators import cache_return

C = None
HANDY_LOGGER_KEY = "handy-logger"
DEFAULT_STYLE = "{"


def init(config_path=None, encoding="utf-8"):
    global C
    C = load_yaml_to_dict(config_path, encoding=encoding)
    import logging.config
    logging.config.dictConfig(C)
    info("{} initialized!", HANDY_LOGGER_KEY, pprint.pformat(C))
    info("{} CONFIG:\n{}", HANDY_LOGGER_KEY, pprint.pformat(C))
    info("{} CONFIG END", HANDY_LOGGER_KEY)


def _assert_initialized():
    assert isinstance(C, dict), \
        "{} has not been initialized. " \
        "You may need to call {}.init() first".format(HANDY_LOGGER_KEY, HANDY_LOGGER_KEY)


@cache_return
def _get_style():
    _assert_initialized()
    style = C.get(HANDY_LOGGER_KEY, {}).get("style", DEFAULT_STYLE)
    assert style in ["{", "%"], "Message format style can only be '{' or '%', " \
                                "now it's: {}".format(style)
    return style


def _pre_format_msg(msg, *args):
    style = _get_style()
    if style == "{":
        return msg.format(*args)
    # Can leave this condition to the built-in logger?
    if style == "%":
        return msg % args


def _log(level, msg, *args, **kwargs):
    """
    Log 'msg % args' or 'msg.format(*args)'
    with the integer severity 'level' on the logger of current module.

    Difficult to support: 'msg.format(*args, **kwargs)'.
    This requires to pop all the keys from kwargs which have been exhausted by msg.
    """
    module_name, _ = get_caller_module_name(stacklevel=2)
    logger = logging.getLogger(module_name)
    msg = _pre_format_msg(msg, *args)
    if "stacklevel" not in kwargs:
        kwargs["stacklevel"] = 3
    logger.log(level, msg, **kwargs)


def critical(msg, *args, **kwargs):
    """
    Log a message with severity 'CRITICAL' on the logger of current module.
    """
    _log(logging.CRITICAL, msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    """
    Log a message with severity 'ERROR' on the logger of current module.
    """
    _log(logging.ERROR, msg, *args, **kwargs)


def exception(msg, *args, exc_info=True, **kwargs):
    """
    Log a message with severity 'ERROR' on the logger of current module,
    with exception information.
    """
    error(msg, *args, exc_info=exc_info, **kwargs)


def warning(msg, *args, **kwargs):
    """
    Log a message with severity 'WARNING' on the logger of current module.
    """
    _log(logging.WARNING, msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    """
    Log a message with severity 'INFO' on the logger of current module.
    """
    _log(logging.INFO, msg, *args, **kwargs)


def debug(msg, *args, **kwargs):
    """
    Log a message with severity 'DEBUG' on the logger of current module.
    """
    _log(logging.DEBUG, msg, *args, **kwargs)
