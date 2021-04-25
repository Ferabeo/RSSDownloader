import confuse 

appName='RSSDownloader'
appConfig='config.yaml'

def getConfig():
    config = confuse.Configuration(appName, __name__)
    config.set_file(appConfig)
    return config