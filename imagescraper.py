#! /usr/bin/env python

import os
import re
import sys
import time
import argparse
import Lib

parser = argparse.ArgumentParser(
    description="Download images from 4chan into a directory hierarchy."
    )

parser.add_argument(
    "links", type=str, nargs="+",
    help="links to 4chan threads or boards"
    )
parser.add_argument(
    "--version", action="version",
    version="%(prog)s v1.0",
    help="show the version of this program and exit"
    )
parser.add_argument(
    "-t", "--threads", metavar="n", type=int, default = 32,
    help="number of threads to use for multi-threading"
    )
parser.add_argument(
    "-o", "--output", metavar="directory", type=str,
    default=".",
    help="where to create the directory hierarchy"
    )
parser.add_argument(
    "-q", "--quiet", action="store_true",
    help="do not print messages to screen"
    )
parser.add_argument(
    "-k", "--keep-names", action="store_true",
    help="keep original names on images"
    )
parser.add_argument(
    "-l", "--listen", nargs="?",
    const="1m", metavar="time",
    help='''download images continually from link,
accepts an optional format string for time where you specify minutes with m and seconds with s
example: \"1m30s\"'''
    )

args = parser.parse_args()
Lib.globals.acquire(args)

def quietly_print(s, outfile=sys.stdout):
    if not args.quiet:
        outfile.write(s + os.linesep)

if not os.path.isdir(args.output):
    print >> sys.stderr, "Error: %s is not a valid directory." % (args.output)
else:
    os.chdir(args.output)

update_interval = 0
if args.listen:
    try:
        seconds = re.search(r"(-?\d*\.?\d*)s", args.listen)
        minutes = re.search(r"(-?\d*\.?\d*)m", args.listen)

        if seconds:
            update_interval += float(seconds.groups()[0])
        if minutes:
            update_interval += float(minutes.groups()[0]) * 60

        if update_interval < 0:
            raise ValueError("Negative update interval %f does not make sense." % (update_interval))
    except Exception as e:
        print >> sys.stderr, "Malformed input: %s is invalid as a format string for time, recieved error: %s" % (
            args.listen, str(e))
        exit(1)

links = []
for link in args.links:
    try:
        links.append(Lib.Link.classify(link))
    except Exception as e:
        quietly_print("Error while processing link %s, will continue if at all possible." % (e))

if not links:
    print >> sys.stderr, "No valid links, exiting with failure."
    exit(1)

pool = Lib.Threads.ThreadPool(args.threads)
Lib.globals.downloadedFiles = []

timer = 0
def report():
    if Lib.globals.downloadedFiles:
        totalBytes = 0
        for file in Lib.globals.downloadedFiles:
            totalBytes += os.path.getsize(file)

        quietly_print("Downloaded %d file(s) (%d bytes) in %f second(s) (%f bytes per second)." % (
                len(Lib.globals.downloadedFiles), totalBytes,
                timer, totalBytes/timer)
                      )

        Lib.globals.downloadedFiles = []

while True:
    try:
        timer = time.time()

        for link in links:
            quietly_print("processing link: %s" % (link))
            pool.push(link)

        quietly_print("waiting for downloads to finish")
        pool.join()

        timer = time.time() - timer

        report()

        if not args.listen:
            break

        if timer < update_interval:
            quietly_print("sleeping for %f seconds" % (update_interval - timer))
            time.sleep(update_interval - timer)
    except:
        exit(0)
