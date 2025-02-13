import unittest

from xpire.cpus.intel_8080 import Intel8080
from xpire.memory import Memory
from xpire.screen import Screen


class TestIntel8080(unittest.TestCase):
    def test_screen(self):
        memory = Memory()
        cpu = Intel8080(memory=memory)

        screen = Screen(width=224, height=256, title="Xpire", scale=3)
        screen.render(cpu)
