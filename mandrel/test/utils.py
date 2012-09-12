import contextlib
import os
import shutil
import tempfile
import mandrel
import unittest

class TestCase(unittest.TestCase):
    def assertIs(self, a, b):
        # python 2.6/2.7 compatibility
        self.assertTrue(a is b)

@contextlib.contextmanager
def tempdir(dir=None):
    """Context manager that yields a temporary directory.  Cleans up afterwards."""
    if dir is not None:
        dir = os.path.realpath(os.path.expanduser(dir))

    path = os.path.realpath(tempfile.mkdtemp(dir=dir))
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)

@contextlib.contextmanager
def chdir(path):
    """Context manager that moves to path in context; returns to original dir afterwards."""
    start_path = os.path.realpath('.')
    try:
        os.chdir(os.path.realpath(os.path.expanduser(path)))
        yield
    finally:
        os.chdir(start_path)

@contextlib.contextmanager
def workdir(dir=None):
    """Context manager that creates a temp dir, moves to it, and yields the path.

    Moves back to original dir and cleans up afterwards."""
    with tempdir(dir) as path:
        with chdir(path):
            yield path


def refresh_bootstrapper():
    if hasattr(mandrel, 'bootstrap'):
        reload(mandrel.bootstrap)
    else:
        __import__('mandrel.bootstrap')

BOOTSTRAP_FILE = 'Mandrel.py'
@contextlib.contextmanager
def bootstrap_scenario(text="", dir=None):
    with workdir(dir=dir) as path:
        bootstrapper = os.path.join(path, BOOTSTRAP_FILE)
        with open(bootstrapper, 'w') as f:
            f.write(text)
        yield path, bootstrapper

