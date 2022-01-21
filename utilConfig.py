import os
import sys
import confuse

APP_NAME = 'RSSDownloader'
APP_CONFIG = 'config.yaml'


def getConfig():
    config = confuse.Configuration(APP_NAME, __name__)
    config.set_file(os.path.join(sys.path[0], APP_CONFIG))
    return config
