#!/usr/bin/env python2
# Imageboard Image Scraper
# written by Truls Edvard Stokke <trulses@gmail.com>

__doc__ = """Imageboard Image Scraper.

Example:
    $ ./imagescraper.py http://boards.4chan.org/g/thread/15898894

    This will create a g/15898894/ directory and download the images to that folder.
    You may also give links to 4chan boards as arguments.

Usage:
  imagescraper.py [-q] [-k] [-p] [-t <num>] [-o <dir>] [-l <time>] <links>...
  imagescraper.py -h | --help
  imagescraper.py --version

Arguments:
  <link>    Links to 4chan threads or boards

Options:
  -h, --help           Show this screen.
  --version            Show version.
  -q, --quiet          Do not print messages to screen
  -k, --keep-names     Keep original image names
  -p, --save-page      Save the thread html as well, to open up later
  -t, --threads <num>  Number of threads to use for multi-threading [default: 32]
  -o, --output <dir>   Where to create the directory hierarchy [default: .]
  -l, --listen <time>  Download images continuiously from given link. Accepts an
                       optional format string where you specify minutes with 'm'
                       and seconds with 's' [example: 1m30s]

Requirements:
  Python2.
"""

# config
_version = 'Imageboard Image Scraper 1.0.0'

import os
import re
import sys
import time
from Lib.ext.docopt import docopt
import Lib

args = docopt(__doc__, version=_version)

Lib.globals.acquire({
    'quiet': args['--quiet'],
    'keep_names': args['--keep-names'],
    'save_page': args['--save-page'],
    'threads': int(args['--threads']),
    'output': args['--output'],
    'listen': args['--listen'],
    'links': args['<links>'],
    })

def quietly_print(s, outfile=sys.stdout):
    if not Lib.globals.quiet:
        outfile.write(s + os.linesep)

if not os.path.isdir(Lib.globals.output):
    print >> sys.stderr, "Error: %s is not a valid directory." % (Lib.globals.output)
else:
    os.chdir(Lib.globals.output)

update_interval = 0
if Lib.globals.listen:
    try:
        seconds = re.search(r"(-?\d*\.?\d*)s", Lib.globals.listen)
        minutes = re.search(r"(-?\d*\.?\d*)m", Lib.globals.listen)

        if seconds:
            update_interval += float(seconds.groups()[0])
        if minutes:
            update_interval += float(minutes.groups()[0]) * 60

        if update_interval < 0:
            raise ValueError("Negative update interval %f does not make sense." % (update_interval))
    except Exception as e:
        print >> sys.stderr, "Malformed input: %s is invalid as a format string for time, recieved error: %s" % (
            Lib.globals.listen, str(e))
        exit(1)

links = []
for link in Lib.globals.links:
    try:
        links.append(Lib.Link.classify(link))
    except Exception as e:
        quietly_print("Error while processing link %s, will continue if at all possible." % (e))

if not links:
    print >> sys.stderr, "No valid links, exiting with failure."
    exit(1)

pool = Lib.Threads.ThreadPool(Lib.globals.threads)
Lib.globals.downloadedFiles = []
Lib.globals.links = links

timer = 0
def report():
    if Lib.globals.downloadedFiles:
        totalBytes = 0
        for file in Lib.globals.downloadedFiles:
            totalBytes += os.path.getsize(file)

        quietly_print("Downloaded %d file(s) (%s) in %f second(s) (%s per second)." % (
                len(Lib.globals.downloadedFiles), Lib.Util.bytes_to_human(totalBytes),
                timer, Lib.Util.bytes_to_human(totalBytes/timer))
        )

        Lib.globals.downloadedFiles = []

while links:
    try:
        timer = time.time()

        for link in links:
            quietly_print("processing link: %s" % (link))
            pool.push(link)

        quietly_print("waiting for downloads to finish")
        pool.join()

        timer = time.time() - timer

        report()

        if not Lib.globals.listen:
            break

        if timer < update_interval:
            quietly_print("sleeping for %f seconds" % (update_interval - timer))
            time.sleep(update_interval - timer)
    except Exception as e:
        quietly_print("Recieved: %s" % (e))
        exit(0)
