#! /usr/bin/env python

import os
import sys
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

args = parser.parse_args()

def quietly_print(s, outfile=sys.stdout):
    if not args.quiet:
        outfile.write(s + os.linesep)

if not os.path.isdir(args.output):
    print >> sys.stderr, "Error: %s is not a valid directory." % (args.output)
else:
    os.chdir(args.output)

links = []
for link in args.links:
    try:
        links.append(Lib.Link.classify(link))
    except Exception as e:
        quietly_print("Error while processing link %s, will continue if at all possible." % (e))

if not links:
    print >> sys.stderr, "No valid links, exiting with failure."
    exit(1)

Lib.globals.acquire(args)

pool = Lib.Threads.ThreadPool(args.threads)

for link in links:
    pool.push(link)

pool.join()
