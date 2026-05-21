import io
import sys
import unittest
from unittest.mock import patch, MagicMock


class SilentTest(unittest.TestCase):
    def setUp(self):
        self._printPatch = patch("builtins.print")
        self._printPatch.start()
        self._realStdout = sys.stdout
        _buf = MagicMock()
        _buf.write = MagicMock()
        _buf.flush = MagicMock()
        _silent = io.StringIO()
        _silent.buffer = _buf
        sys.stdout = _silent

    def tearDown(self):
        self._printPatch.stop()
        sys.stdout = self._realStdout
