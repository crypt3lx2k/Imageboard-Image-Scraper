#! /usr/bin/env python

from iwi.core      import classify
from iwi.core      import Thread
from iwi.core      import WebEntity
from iwi.threading import Pool
from iwi.web       import all_boards

from common import logger
from common import parameters

def prune_cache (*links):
    """
    Prunes 404ed entries from the internal WebEntity.webcache.

    This function accepts only links to boards and pages.
    If no links are given every board on 4chan is checked.
    """
    pool = Pool(num_threads=parameters.num_threads)

    def work (unit):
        if isinstance(unit, Thread):
            return unit

        logger.info('working %r', unit)
        for e in unit.process():
            pool.push(work, e)

        return unit

    if not links:
        links = all_boards

    for link in map(classify, links):
        if isinstance(link, Thread):
            logger.warn('ignoring %s', link)

        pool.push(work, link)

    pool.join()
    logger.info('Join complete, pruning cache.')

    live = pool.get_results()
    pool.close()

    live = map(lambda alive : alive.apiurl  , live)
    live = map(WebEntity.webcache.url_to_key, live)
    live = set(live)

    keys = WebEntity.webcache.keys()
    keys = filter (
        lambda key : key not in live,
        keys
    )

    for key in keys:
        logger.info('pruning %s', key)
        WebEntity.webcache.remove_key(key)

if __name__ == '__main__':
    from common import OfflineParser

    parser = OfflineParser (
        description='Prunes 404ed entries from the web cache.',
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
    prune_cache(*args.link)
    parser.post_process(args, force_cache_write=True)
