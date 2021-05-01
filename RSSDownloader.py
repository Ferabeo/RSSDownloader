# Default libs
import os
import sys
import re

# Custom libs
import requests
import feedparser
from pathlib import Path
from pathvalidate import sanitize_filename

# Locally defined
from utilJson import readJsonFile, writeJsonFile
from utilConfig import getConfig


class RSSDownloader(object):
    '''
    RSSDownloader download all .torrent files from RSS feed
    history of downloaded file is kept on rss-hist.txt
    '''
    hist = 'rss-hist.txt'		# Location of history file
    inc = 'rss-inc.txt'		# Location of incoming links file

    def __init__(self, rssFeed):
        '''Return a RSSDownloader object'''

        # RSS Feed
        self.name = rssFeed.get('name')
        self.rssUrl = rssFeed.get('url')
        self.filterRegex = rssFeed.get('filter', '.*')
        self.filterPattern = re.compile(self.filterRegex)
        self.folderName = sanitize_filename(self.name)

        # -------------------------- #
        #  Create files and folders
        # -------------------------- #
        self.torrentFolder = os.path.join(
            sys.path[0], getConfig()['config']['torrentFolder'].get())

        self.Historyfolder = os.path.join(
            sys.path[0], getConfig()['config']['historyFolder'].get(), self.folderName)

        # Location of incoming links file
        self.inc = '{0}/{1}'.format(self.Historyfolder, RSSDownloader.inc)
        # Location of history link file
        self.hist = '{0}/{1}'.format(self.Historyfolder, RSSDownloader.hist)
        self.createFolderFiles()

        # -------------------------- #
        # Load File History
        # -------------------------- #
        self.data = None
        self.incData = readJsonFile(self.inc)
        self.histData = readJsonFile(self.hist)

    def createFolderFiles(self):
        Path(self.torrentFolder).mkdir(parents=True, exist_ok=True)
        Path(self.Historyfolder).mkdir(parents=True, exist_ok=True)
        Path(self.inc).touch(exist_ok=True)
        Path(self.hist).touch(exist_ok=True)

    def start(self):
        # ----------------------- #
        # --- get RSS content --- #
        # ----------------------- #
        self.getRssData()

        # --------------------------- #
        # --- Determine Incomming --- #
        # --------------------------- #
        self.buildInc()
        self.cleanInc()
        writeJsonFile(self.inc, self.incData)

        # ------------------ #
        # ---- DOWNLOAD ---- #
        # ------------------ #
        self.downloadTorrents()

    def getRssData(self):
        try:
            data = feedparser.parse(self.rssUrl)

            if data.status != 200:
                sys.exit('Error getting RSS data - HTTP Code {}'.format(data.status))
            if data.bozo:
                sys.exit('Error getting RSS data - Bozo parse error {}'.format(data.bozo_exception))

        except Exception as e:
            sys.exit('Error getting RSS data - {}'.format(e))

        self.data = data

    def buildInc(self):
        for post in self.data.entries:
            if post.title not in self.incData and self.allowedByFilter(
                    post.title):
                self.incData[post.title] = {
                    'link': post.link,
                    'published': post.published,
                }

    def cleanInc(self):
        postDelete = []
        for post in self.incData:
            if post in self.histData:
                postDelete.append(post)

        for post in postDelete:
            del self.incData[post]

    def allowedByFilter(self, title):
        if self.filterPattern.search(title):
            return True
        return False

    def downloadTorrents(self):
        if len(self.incData.items()) == 0:
            print('{0} - already up to date.'.format(self.name))

        # For each RSS entry
        for inc, incData in self.incData.items():
            if inc not in self.histData:
                # Download file
                statusCode = self.downloadTorrent(inc, incData)
                # Save history to file
                if statusCode == 200:
                    self.histData[inc] = incData
                    writeJsonFile(self.hist, self.histData)

    def downloadTorrent(self, inc, incData):
        destFile = '{}.torrent'.format(sanitize_filename(inc))
        destFullPath = os.path.join(self.torrentFolder, destFile)

        if os.path.isfile(destFullPath) and os.path.getsize(destFullPath) > 0:
            print('Not downloading. File already present on disk {}'.format(
                destFullPath))
            return 200

        try:
            print(
                'Downloading to {} - {}'.format(destFullPath, incData['link']))
            resp = requests.get(incData['link'])

            if resp.status_code == 200:
                open(destFullPath, 'wb').write(resp.content)
        except Exception as e:
            sys.exit('Error getting torrent file - {}'.format(e))

        return resp.status_code

    def infos(self):
        print('{0}\n- PATH: {1}\n- RSS: {2}'.format(self.name,
              self.Historyfolder, self.rssUrl))
