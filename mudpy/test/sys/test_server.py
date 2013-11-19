import unittest
from ...sys import wireframe

def setup_module():
    wireframe.__path__ = 'example'
    wireframe.preload()

class TestServer(unittest.TestCase):

    def setUp(self):
        pass
    
    def testCreateMudInstance(self):
        pass
