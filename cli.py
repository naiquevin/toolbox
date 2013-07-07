"""Some random utils for writing command line scripts"""

import os
import sys
from contextlib import contextmanager


class CliError(Exception):
    """A base cli exception"""
    pass


@contextmanager
def read_input(filepath, stdin):
    """Contextmanager that gets a file like object as source

    If filepath is not None, then it will open the file and return the
    file object. In the end, takes care of closing it. Reads standard
    input if stdin is True Raises an exception if both above cases
    fail

    :param filepath: str

    :param stdin: bool

    :rtype: file like object to be used with `with` keyword

    """
    if filepath is not None:
        f = open(os.path.abspath(filepath))
        yield f
        f.close()
    elif stdin:
        yield sys.stdin
    else:
        raise CliError(
            'At least one of log file path or'
            'input from stdin is required'
        )

