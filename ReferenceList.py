import os
import sys
import re
from pathlib import Path
from pathvalidate import sanitize_filename

from utilJson import readJsonFile, writeJsonFile
from utilConfig import getConfig


class ReferenceList(object):
    '''
    ReferenceList keep track of all downloads titles
    to avoid multiples download between lists
    '''

    def __init__(self, fileName):
        '''Return a ReferenceList object'''

        # ReferenceList Infos
        self.name = 'ReferenceList'

        # keep all text before year 1800 to 2199
        self.filter_pattern = re.compile('(.*)(?:(?:18|19|20|21)[0-9]{2}).*')

        # ------ #
        #  File  #
        # ------ #
        self.ref = os.path.join(
            sys.path[0],
            sanitize_filename(fileName))
        self.create_file()

        # -------------------------- #
        # Load Inc and History File  #
        # -------------------------- #
        self.ref_data = readJsonFile(self.ref)

        self.count = len(self.ref_data)

    def save(self):
        writeJsonFile(self.ref, self.ref_data)

    def sanitize_name(self, name):
        '''Parse the name to keep name of movie only'''
        parsed = self.filter_pattern.search(name)
        return parsed.group(1) if parsed else name

    def replace_non_aplha_chars(self, name):
        return re.sub("[^0-9a-zA-Z]+", " ", name).strip()

    def add(self, name):
        correct_name = self.replace_non_aplha_chars(self.sanitize_name(name))
        self.ref_data[correct_name] = name

    def present(self, name):
        correct_name = self.replace_non_aplha_chars(self.sanitize_name(name))
        return False if correct_name in self.ref_data else True

    def create_file(self):
        '''Create file'''
        Path(self.ref).touch(exist_ok=True)

    def infos(self):
        '''Provide class infos'''
        print('{0}\n- PATH: {1}\n- nb Entries: {2}'.format(self.name,
                                                           self.ref,
                                                           self.count))
