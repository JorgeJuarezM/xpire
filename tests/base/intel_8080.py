import unittest

from xpire.cpus.intel_8080 import Intel8080


class Intel8080_Base(unittest.TestCase):
    def setUp(self):
        self.cpu = Intel8080()
