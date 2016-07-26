#! /usr/bin/env python

from iwi.core      import classify
from iwi.core      import Thread
from iwi.threading import Pool
from iwi.web       import all_boards

from common import logger
from common import parameters

def build_cache (*links):
    """
    Builds up the internal WebEntity.webcache with a snapshot of the provided
    URLs.

    If no URLs are given, it will attempt to update the cache with a snapshot
    of the entirety of 4chan.
    """
    pool = Pool(num_threads=parameters.num_threads)

    def work (unit):
        logger.info('working %r', unit)

        if isinstance(unit, Thread):
            unit.download()
        else:
            for e in unit.process():
                pool.push(work, e)

    if not links:
        links = all_boards

    for link in map(classify, links):
        pool.push(work, link)
        pool.join()

    logger.info('Join complete.')

if __name__ == '__main__':
    from common import CommonParser

    parser = CommonParser (
        description='Builds the web cache.',
        epilog='if no links are given all of 4chan is scraped'
    )

    parser.add_argument (
        'link', nargs='*',
        help='boards/pages/threads, may either be full URLs or names like /g/'
    )

    args = parser.parse_args()

    if parser.sanity_check(args):
        exit(1)

    parser.pre_process(args)
    build_cache(*args.link)
    parser.post_process(args)
