import unittest
from mudpy.mudpy.affect import Affect
from mudpy.mudpy.debug import DebugException

class TestAffect(unittest.TestCase):

    def setUp(self):
        self.affect = Affect()

    def testCountdownTimeount(self):
        self.affect.timeout = 100
        self.affect.countdown_timeout()
        self.assertEquals(self.affect.timeout, 99)
