#!/usr/bin/env python3

import sys
import apprise

import RSSDownloader
import ReferenceList
from utilConfig import getConfig

if sys.version_info[0] < 3:
    raise Exception("Python 3 is mandatory")


def main(argv):
    config = getConfig()['config']
    rssFeeds = config['rss'].get()

    # List of references for all RSS
    refList = ReferenceList.ReferenceList(config['referenceList'].get())

    # Apprise notification
    appRise = apprise.Apprise()
    appRise.add(config['appRiseUrl'].get())

    for feed in rssFeeds:
        currentFeed = RSSDownloader.RSSDownloader(
            feed, config, refList, appRise)
        # currentFeed.infos()
        currentFeed.start()

    # Save references to file
    refList.infos()
    refList.save()


if __name__ == '__main__':
    main(sys.argv)
