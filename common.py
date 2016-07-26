"""
This file holds things that the various programs have in common.
"""
import argparse
import logging

from iwi.core import WebEntity
from iwi.web  import Links

from defaults import defaults

__all__ = ['CommonParser', 'OfflineParser', 'TripcodeParser',
           'logger', 'parameters']

logger = logging.getLogger('')
logger.setLevel(logging.INFO)

default_handler = logging.StreamHandler(defaults['log_file'])
logger.addHandler(default_handler)

parameters = argparse.Namespace(**defaults)

class CommonParser (argparse.ArgumentParser):
    """
    This is an ArgumentParser that adds common arguments based on the
    default values.
    """
    def __init__ (self, *args, **kwargs):
        """
        Initializes an instance adding common arguments.
        """
        super(CommonParser, self).__init__(*args, **kwargs)

        self.add_argument (
            '--cache-file',
            metavar='file', type=str, default=defaults['cache_file'],
            help='which file to use as cache, defaults to {cache_file}'.format (
                **defaults
            )
        )

        self.add_argument (
            '--log-file',
            metavar='file',
            type=argparse.FileType('a'), default=defaults['log_file'],
            help='log file, defaults to {log_file.name}'.format (
                **defaults
            )
        )

        self.add_argument (
            '--num-threads',
            metavar='n', type=int, default=defaults['num_threads'],
            help='how many threads to use, defaults to {num_threads}'.format (
                **defaults
            )
        )

        self.add_argument (
            '--debug',
            action='store_false' if defaults['debug'] else 'store_true',
            help='toggle debug information, defaults to {debug}'.format (
                **defaults
            )
        )

        self.add_argument (
            '--https',
            action='store_false' if defaults['https'] else 'store_true',
            help='toggle HTTPS, defaults to {https}'.format (
                **defaults
            )
        )

        self.add_argument (
            '--quiet',
            action='store_false' if defaults['quiet'] else 'store_true',
            help='toggle quiet mode, defaults to {quiet}'.format (
                **defaults
            )
        )

    def parse_args (self, args=None, parameters=parameters):
        return super(CommonParser, self).parse_args (
            args=args, namespace=parameters
        )

    def post_process (self, parameters=parameters):
        """
        Acts on tdt based on parameter list after program has been ran.
        """
        WebEntity.webcache.dump(parameters.cache_file)

    def pre_process (self, parameters=parameters):
        """
        Acts on tdt based on parameter list to set up program conditions.
        """
        if parameters.debug:
            logger.setLevel(logging.DEBUG)

        if parameters.quiet:
            logger.setLevel(logging.WARNING)

        if parameters.https:
            Links.scheme = 'https'

        if parameters.log_file is not defaults['log_file']:
            logger.removeHandler(default_handler)
            logger.addHandler (
                logging.StreamHandler (parameters.log_file)
            )

        WebEntity.webcache.load(parameters.cache_file)

    def sanity_check (self, parameters=parameters):
        """
        Returns whether the parameter list is insane or not.
        """
        if parameters.debug and parameters.quiet:
            logger.error('both --debug and --quiet set')
            return True

        return False

class OfflineParser (CommonParser):
    """
    Adds handling for offline mode to the CommonParser.
    """
    def __init__ (self, *args, **kwargs):
        super(OfflineParser, self).__init__(*args, **kwargs)

        self.add_argument (
            '--offline',
            action='store_false' if defaults['offline'] else 'store_true',
            help='toggle offline mode, defaults to {offline}'.format (
                **defaults
            )
        )

    def post_process (self, parameters=parameters, force_cache_write=False):
        """
        Acts on tdt based on parameter list after program has been ran.
        """
        if not parameters.offline or force_cache_write:
            WebEntity.webcache.dump(parameters.cache_file)

    def pre_process (self, parameters=parameters):
        """
        Acts on tdt based on parameter list to set up program conditions.
        """
        super(OfflineParser, self).pre_process(parameters=parameters)

        if parameters.offline:
            WebEntity.webcache.set_offline_mode()

            if (parameters.num_threads != defaults['num_threads'] and
                parameters.num_threads != 1):
                logger.warning (
                    'set --num-threads will be ignored due to offline mode'
                )

            parameters.num_threads = 1
