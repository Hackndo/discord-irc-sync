import json
import logging
import os
import sys


def replace_all(text, l):
    for t in l:
        text = text.replace(t[0], t[1])
    return text


def is_included(a, b):
    """
    Return 0 if a is included in b
    Return -1 if a intersects b but a not included in b and b not included in a
    Return 1 else
    """
    if a[1] >= b[1] and a[2] <= b[2]:
        return 0
    elif a[1] > b[1] and a[2] > b[2] or a[1] < b[1] and a[2] < b[2]:
        return -1
    else:
        return 1


def read_config(config_file=None):
    config_file = os.path.join("config", "config.json") if config_file is None else config_file

    if not os.path.isfile(config_file):
        sys.exit("File %s doesn't exist" % config_file)

    with open(config_file, encoding="utf-8") as f:
        return json.loads(f.read())


def get_logger(module_name, log_level=logging.INFO):
    from discord.utils import _ColourFormatter, stream_supports_colour

    logger = logging.getLogger(module_name)
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    if stream_supports_colour(handler.stream):
        formatter = _ColourFormatter()
    else:
        formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
