"""
This file holds the default values for the various programs.
"""
import sys

__all__ = ['defaults']

defaults = {
    # filenames
    'cache_file'  : 'bin/cache.bin',
    'log_file'    : sys.stderr,

    # values
    'num_threads' : 16,

    # flags
    'debug'       : False,
    'https'       : True,
    'offline'     : False,
    'quiet'       : False
}
