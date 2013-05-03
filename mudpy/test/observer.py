import unittest
from mudpy.mudpy.observer import Observer

class TestObserver(unittest.TestCase):

    def setUp(self):
        self.observer = Observer()
    
    def test_attach(self):
        self.observer.attach('testevent', self.test_attach)
        self.assertEquals(1, len(self.observer.observers['testevent']))
    
    def test_detach(self):
        self.observer.attach('testevent', self.test_attach)
        self.observer.detach('testevent', self.test_attach)
        self.assertEquals(0, len(self.observer.observers['testevent']))
    
    def test_dispatch_without_args(self):
        def success(args):
            raise SuccessException
        def testCase():
            self.observer.dispatch('testevent')
        self.observer.attach('testevent', success)
        self.assertRaises(SuccessException, testCase)
    
    def test_dispatch_with_args(self):
        def success(args):
            if args['message'] == 'fire_success':
                raise SuccessException
        def testCase():
            self.observer.dispatch('testevent', message='fire_success')
        self.observer.attach('testevent', success)
        self.assertRaises(SuccessException, testCase)
    
    def test_empty_dispatch(self):
        self.observer.dispatch('testevent')

class SuccessException(Exception): pass
