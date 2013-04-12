import unittest
from mudpy.mudpy.observer import Observer

class TestObserver(unittest.TestCase):

	def setUp(self):
		self.observer = Observer()
	
	def testAttach(self):
		self.observer.attach('testevent', self.testAttach)
		self.assertEquals(1, len(self.observer.observers['testevent']))
	
	def testDetach(self):
		self.observer.attach('testevent', self.testAttach)
		self.observer.detach('testevent', self.testAttach)
		self.assertEquals(0, len(self.observer.observers['testevent']))
	
	def testDetachAll(self):
		self.observer.attach('testevent', self.testAttach)
		self.observer.attach('testevent', self.testDetach)
		self.observer.detachAll()
		self.assertEquals(0, len(self.observer.observers))
	
	def testDispatch(self):
		def success(*args):
			raise SuccessException
		self.observer.attach('testevent', success)
		try:
			self.observer.dispatch('testevent')
			self.fail("failed to raise SuccessException in testDispatch")
		except SuccessException: pass
		try:
			self.observer.dispatch(testevent = self)
			self.fail("failed to raise SuccessException in testDispatch")
		except SuccessException: pass

class SuccessException(Exception): pass
