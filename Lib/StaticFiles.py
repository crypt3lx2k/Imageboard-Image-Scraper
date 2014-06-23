import os as _os
import sys as _sys
import re as _re
import time as _time
import urllib2 as _urllib2
import shutil as _shutil

class StaticFileHandler(object):
    """Handle static files."""
    def __init__(self):
        self.base_dir = _os.path.expanduser('~/.config/imageboard-image-scraper/static')
        if not _os.path.exists(self.base_dir):
            _os.makedirs(self.base_dir)
        self.expiry_seconds = 60 * 60 * 3  # 3 hours

    def download(self, url, output_folder):
        """Download given file, if it's older than our expiration time."""
        filename = self.url_to_filename(url)
        full_filename = _os.path.join(self.base_dir, filename)
        folder = _os.path.join(self.base_dir, filename.rsplit('/', 1)[0])
        
        if not _os.path.exists(folder):
            _os.makedirs(folder)

        file_modified_timestamp = 0  # all else fails, we assume 0 so it always fails our check
        if _os.path.exists(full_filename):
            file_modified_timestamp = _os.path.getmtime(full_filename)

        # download the file
        if self.file_expired(file_modified_timestamp):
            ## d/l lel
            try:
                content = _urllib2.urlopen('https:{}'.format(url)).read()
                with open(full_filename, 'wb') as output_file:
                    output_file.write(content)
            except _urllib2.HTTPError as e:
                return False
            except _urllib2.URLError as e:
                return False

        # copy file to output
        output_folder = _os.path.abspath(output_folder)
        full_output_folder = _os.path.join(output_folder, filename.rsplit('/', 1)[0])
        full_output_filename = _os.path.join(output_folder, filename)

        if not _os.path.exists(full_output_folder):
            _os.makedirs(full_output_folder)

        _shutil.copyfile(full_filename, full_output_filename)

    def file_expired(self, modified_time):
        """Given modified time (as unix timestamp), return True for expired or False for new enough to be OK."""
        expiry_time = _time.time() - self.expiry_seconds

        if modified_time < expiry_time:
            return True
        else:
            return False

    def url_to_filename(self, url):
        """Convert URL to our filename."""
        filename = url.lstrip('http:').lstrip('https:').lstrip('/')
        return filename

    def extract_static_urls(self, content):
        """Extract the static URLs from the given file."""
        return set(_re.findall(r"((?:https?)?//s\.4cdn\.org/[a-zA-Z0-9-/\.]+(?:ico|css|js))", content))
