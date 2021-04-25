#!/usr/bin/env python3

import json
import sys
import os
import datetime

import RSSDownloader
from utilConfig import getConfig

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")


def main(argv):
    config = getConfig()
    rssFeeds = config['config']['rss'].get()

    for feed in rssFeeds:
        currentFeed = RSSDownloader.RSSDownloader(feed)
        # currentFeed.infos()
        currentFeed.start()


if __name__ == '__main__':
    main(sys.argv)
