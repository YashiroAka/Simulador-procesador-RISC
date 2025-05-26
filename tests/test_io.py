import unittest
from io import interrupt_handler, devices

class TestIO(unittest.TestCase):
    def test_interrupt_handler(self):
        ih = interrupt_handler.InterruptHandler()
        ih.trigger("INT_1")
        self.assertEqual(ih.handle_next(), "INT_1")
