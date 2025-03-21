from xpire.cpus.intel_8080 import Intel8080
import unittest

class Intel8080_Base(unittest.TestCase):
    def setUp(self):
        self.cpu = Intel8080()