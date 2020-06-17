import os
import shelve

from threading import RLock
from queue import Queue, Empty
from collections import defaultdict
from time import sleep

from utils import get_logger, get_urlhash, normalize, cleanURL
from urllib.parse import urlparse
from scraper import is_valid

class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.available = set()
        self.inUse = set()
        self.file = open('goodlinks.txt', 'w')
        self.to_be_downloaded = defaultdict(Queue)
		       
        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        if restart:
            for url in self.config.seed_urls:
                cleaned = cleanURL(url)
                if cleaned:
                    self.available.add(cleaned)
                    self.add_url(url)
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    cleaned = cleanURL(url)
                    if cleaned:
                        self.available.add(cleaned)
                        self.add_url(url)

    def __del__(self):
        self.file.close()

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save)
        tbd_count = 0
        for url, completed in self.save.values():
            if not completed and is_valid(url):
                cleaned = cleanURL(url)
                if cleaned:
                    self.to_be_downloaded[cleaned].put(url, block=False)
                    tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")


    def get_tbd_url(self, base):
        try:
            return self.to_be_downloaded[base].get(block=False)
        except Empty:
            with RLock():
                del self.to_be_downloaded[base]
                self.inUse.remove(base)
            return None

    def get_new_target(self):
        while not self.available and self.inUse:
            sleep(1)
        if not self.available and not self.inUse:
            return None
        with RLock():
            target = self.available.pop()
            self.inUse.add(target)
        return target
			
	
	
    def add_url(self, url):
        url = normalize(url)
        base = cleanURL(url)
        if base:
            urlhash = get_urlhash(url)
            if urlhash not in self.save:
                self.save[urlhash] = (url, False)
                self.save.sync()
                self.to_be_downloaded[base].put(url, block=False)
                self.file.write(url + '\n')
                if base not in self.inUse:
                    self.available.add(base)
    
    def mark_url_complete(self, url):
        urlhash = get_urlhash(url)
        if url and urlhash not in self.save:
            # This should not happen.
            self.logger.error(
                f"Completed url {url}, but have not seen it before.")

        self.save[urlhash] = (url, True)
        self.save.sync()
