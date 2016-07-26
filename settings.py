"""
Configuration storage/management
"""

import json
import os
import threading

cfglock = threading.Lock()
cfgdir = os.path.abspath(os.path.dirname(__file__))
cfgfile = os.path.join("settings.json")
cfg = None


def get():
    """
    Get the configs from disk (if needed)
    :return:
    """
    global cfg
    with cfglock:
        if not cfg:
            with open(cfgfile, "rb") as cfgfh:
                cfg = json.load(cfgfh)
    return dict(cfg)


def set(cfgdata):
    """
    Set the configs, and save them to disk
    :param cfgdata:
    :return:
    """
    global cfg
    with cfglock:
        cfg = cfgdata
        with open(cfgfile, "wb") as cfgfh:
            json.dump(cfgdata, cfgfh)
