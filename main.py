#!/usr/bin/env python3

import sys
import os
import datetime

import RSSDownloader
import ReferenceList
from utilConfig import getConfig

if sys.version_info[0] < 3:
    raise Exception("Python 3 is mandatory")

def main(argv):
    config = getConfig()['config']
    rssFeeds = config['rss'].get()

    referenceListEnabled = config['referenceListEnabled'].get()

    if referenceListEnabled:
        refList = ReferenceList.ReferenceList(config['referenceList'].get())

    for feed in rssFeeds:
        currentFeed = RSSDownloader.RSSDownloader(feed, config, refList)
        # currentFeed.infos()
        currentFeed.start()

        for title in currentFeed.get_downloaded_titles():
            refList.add(title)

    if referenceListEnabled:
        refList.infos()
        refList.save()

if __name__ == '__main__':
    main(sys.argv)
