import confuse
import os
import sys


appName = 'RSSDownloader'
appConfig = 'config.yaml'


def getConfig():
    config = confuse.Configuration(appName, __name__)
    config.set_file(os.path.join(sys.path[0], appConfig))
    return config
