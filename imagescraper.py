#! /usr/bin/env python

import os
import time

from iwi.core      import classify
from iwi.core      import Post
from iwi.threading import Pool

from common import logger
from common import parameters

def get_filename (directory, post, keep_names=False):
    """
    Returns the path where the downloaded image should be written.
    """
    return os.sep.join ((
        directory, post.board, str(post.thread),
        (post.image.filename if keep_names else str(post.image.tim)) + \
            post.image.ext
    ))

def scrape_images (directory, keep_names, *links):
    """
    Downloads images from links.
    """
    pool = Pool(num_threads=parameters.num_threads)

    def work (unit):
        if isinstance(unit, Post):
            if not unit.image:
                return

            filename = get_filename (
                directory, unit, keep_names
            )

            if not os.path.exists(filename):
                logger.info('downloading %s', unit.image)
                image_data = unit.image.download(bypass_cache=True)

                return filename, image_data

            logger.debug('%s already downloaded', filename)

            return

        logger.info('working %r', unit)
        for e in unit.process():
            pool.push(work, e)

    for link in map(classify, links):
        pool.push(work, link)
    pool.join()

    logger.info('Join complete.')

    downloaded = pool.get_results()
    pool.close()

    logger.info('Setting up directories')

    directories = set (
        map (
            lambda t : os.path.split(t[0])[0],
            downloaded
        )
    )

    for directory in directories:
        if not os.path.exists(directory):
            logger.debug('making directory %s', directory)
            os.makedirs(directory)

    logger.info('Writing images to disk.')

    for filename, image_data in downloaded:
        with open(filename, 'w') as outfile:
            outfile.write(image_data)

if __name__ == '__main__':
    from common import CommonParser

    parser = CommonParser (
        description='Scrapes images from the given 4chan links.'
    )

    parser.add_argument (
        'link', nargs='+',
        help='boards/pages/threads, may either be full URLs or names like /g/'
    )

    parser.add_argument (
        '-o', '--output',
        metavar='directory',
        default='.',
        help='where to create the directory hierarchy, defaults to \'.\''
    )

    parser.add_argument (
        '-k', '--keep-names', action='store_true',
        help='keep original file names on images, defaults to False'
    )

    parser.add_argument (
        '-l', '--listen', nargs='?',
        const=60.0, metavar='time', type=float,
        help='download images continually from link, accepts an optional time given in seconds, defaults to 60.0'
    )

    args = parser.parse_args()

    if parser.sanity_check(args):
        exit(1)

    parser.pre_process(args)

    while True:
        timer = time.time()
        scrape_images(args.output, args.keep_names, *args.link)
        timer = time.time() - timer

        if not args.listen:
            break

        if timer < args.listen:
            logger.info('sleeping for %f seconds', args.listen - timer)
            time.sleep(args.listen - timer)

    parser.post_process(args)
