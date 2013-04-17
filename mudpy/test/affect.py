import unittest
from mudpy.mudpy.affect import Affect
from mudpy.mudpy.debug import DebugException

class TestAffect(unittest.TestCase):

	def setUp(self):
		self.affect = Affect()

	def testStartOnReceiverWithFunctionsDefined(self):
		def test():
			self.affect.start(None)
		self.assertRaises(DebugException, test)
