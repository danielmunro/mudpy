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
		def testCase1():
			self.observer.dispatch('testevent')
		def testCase2():
			self.observer.dispatch(testevent = self)
		self.observer.attach('testevent', success)
		self.assertRaises(SuccessException, testCase1)
		self.assertRaises(SuccessException, testCase2)
	
	def testDispatchForEventWithNoListeners(self):
		self.observer.dispatch('testevent')

class SuccessException(Exception): pass
