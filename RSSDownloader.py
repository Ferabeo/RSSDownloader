import os
import sys
import re
from datetime import datetime
from pathlib import Path
import requests
import feedparser
from pathvalidate import sanitize_filename

from utilJson import readJsonFile, writeJsonFile
from utilConfig import getConfig


class RSSDownloader(object):
    '''
    RSSDownloader download all .torrent files from RSS feed
    history of downloaded file is kept on rss-hist.txt
    '''
    hist = 'rss-hist.txt'       # Location of history file
    inc = 'rss-inc.txt'     # Location of incoming links file

    def __init__(self, rssFeed, config, referenceList):
        '''Return a RSSDownloader object'''

        # -------------- #
        #  Informations  #
        # -------------- #
        # RSS Feed
        self.name = rssFeed.get('name')
        self.rss_url = rssFeed.get('url')
        self.filter_pattern = re.compile(rssFeed.get('filter', '.*'))
        self.referenceList = referenceList

        # Config
        self.config = config
        self.not_older_than = datetime.strptime(
            self.get_attr('notOlderThan'),
            self.get_attr('notOlderThanFormat'))

        # ------------------- #
        #  Files and folders  #
        # ------------------- #
        self.torrent_folder = os.path.join(
            sys.path[0], self.get_attr('torrentFolder'))

        self.history_folder = os.path.join(
            sys.path[0], self.get_attr('historyFolder'),
            sanitize_filename(self.name))

        # Location of incoming links file
        self.inc = '{0}/{1}'.format(self.history_folder, RSSDownloader.inc)
        # Location of history link file
        self.hist = '{0}/{1}'.format(self.history_folder, RSSDownloader.hist)
        self.create_folder_files()

        # -------------------------- #
        # Load Inc and History File  #
        # -------------------------- #
        self.data = None
        self.inc_data = readJsonFile(self.inc)
        self.hist_data = readJsonFile(self.hist)

    def start(self):
        '''Loop over RSS config to download .torrents files'''
        # ----------------------- #
        # --- get RSS content --- #
        # ----------------------- #
        self.get_rss_data()

        # --------------------------- #
        # --- Determine Incomming --- #
        # --------------------------- #
        self.build_inc()
        self.clean_inc()
        writeJsonFile(self.inc, self.inc_data)

        # ------------------ #
        # ---- DOWNLOAD ---- #
        # ------------------ #
        self.download_torrents()

    def get_rss_data(self):
        '''Retrieve RSS Content'''
        try:
            data = feedparser.parse(self.rss_url)
            self.validate_rss_data(data)

        except Exception as exception:
            sys.exit('Error getting RSS data - {}'.format(exception))

        self.data = data

    def validate_rss_data(self, data):
        '''Validate RSS Content'''
        try:
            if data.status != 200:
                sys.exit(
                    'Error getting RSS data - HTTP Code {}'.format(data.status))
            if data.bozo:
                sys.exit(
                    'Error getting RSS data - Bozo parse error {}'.format(data.bozo_exception))
            if "error" in data.get('feed'):
                sys.exit(
                    'Error getting RSS data - Feed is not correct {}'.format(data.get('feed').get('error')))
        except Exception as exception:
            sys.exit('Error checking data - {}'.format(exception))

    def build_inc(self):
        '''Build rss-inc.txt files'''
        for post in self.data.entries:
            if (post.title not in self.inc_data
                    and self.allowed_by_filter(post.title)
                    and self.allowed_by_date_limit(post.published)
                    and self.referenceList.present(post.title)):
                self.inc_data[post.title] = {
                    'link': post.link,
                    'published': post.published,
                }
                # Add movie name to list of downloaded titles
                self.referenceList.add(post.title)

    def clean_inc(self):
        '''Check rss-hist.txt to remove known items'''
        post_delete = []
        for post in self.inc_data:
            if post in self.hist_data:
                post_delete.append(post)

        for post in post_delete:
            del self.inc_data[post]

    def allowed_by_filter(self, title):
        '''Check regex filter of RSS entry config'''
        if self.filter_pattern.search(title):
            return True
        return False

    def allowed_by_date_limit(self, published):
        '''Check item is not older than notOlderThan config parameter'''
        if self.not_older_than < datetime.strptime(
                published, self.get_attr('notOlderThanFormat')):
            return True
        return False

    def download_torrents(self):
        '''Download items in rss-inc.txt and
        if sucessfull write rss-hist.txt'''
        if len(self.inc_data.items()) == 0:
            print('{0} - already up to date.'.format(self.name))

        # For each RSS entry
        for inc, inc_data in self.inc_data.items():
            if inc not in self.hist_data:
                # Download file
                status_code = self.download_torrent(inc, inc_data)
                # Save history to file
                if status_code == 200:
                    self.hist_data[inc] = inc_data
                    writeJsonFile(self.hist, self.hist_data)

    def download_torrent(self, inc, inc_data):
        '''Download .torrent and write to file'''
        dest_file = '{}.torrent'.format(sanitize_filename(inc))
        dest_full_path = os.path.join(self.torrent_folder, dest_file)

        if os.path.isfile(dest_full_path) and os.path.getsize(
                dest_full_path) > 0:
            print('Not downloading. File already present on disk {}'.format(
                dest_full_path))
            return 200

        try:
            print(
                'Downloading to {} - {}'.format(dest_full_path, inc_data['link']))
            resp = requests.get(inc_data['link'])

            if resp.status_code == 200:
                open(dest_full_path, 'wb').write(resp.content)
        except Exception as exception:
            sys.exit('Error getting torrent file - {}'.format(exception))

        return resp.status_code

    def get_attr(self, attribute_name):
        '''Get config attribute named attribute_name'''
        if attribute_name not in self.config:
            sys.exit(
                'Error attribute {} not found in config'.format(attribute_name))
        return self.config[attribute_name].get()

    def create_folder_files(self):
        '''Create folder and files'''
        Path(self.torrent_folder).mkdir(parents=True, exist_ok=True)
        Path(self.history_folder).mkdir(parents=True, exist_ok=True)
        Path(self.inc).touch(exist_ok=True)
        Path(self.hist).touch(exist_ok=True)

    def infos(self):
        '''Provide class infos'''
        print('{0}\n- PATH: {1}\n- RSS: {2}'.format(self.name,
                                                    self.history_folder, self.rss_url))
