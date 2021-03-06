import unittest, re
from mudpy.mudpy import actor

class TestActor(unittest.TestCase):

    def setUp(self):
        pass
    
    def testName(self):
        self.assertTrue(actor.User.is_valid_name("albatross"))
        # too long
        self.assertFalse(actor.User.is_valid_name("albatrossmonkey"))
        # too short
        self.assertFalse(actor.User.is_valid_name("c"))
        # digits
        self.assertFalse(actor.User.is_valid_name("9digit"))
        self.assertFalse(actor.User.is_valid_name("dig1it"))
        # punctuation
        self.assertFalse(actor.User.is_valid_name("punc.t"))
        self.assertFalse(actor.User.is_valid_name("punct;"))
        self.assertFalse(actor.User.is_valid_name("pu-nct"))
        self.assertFalse(actor.User.is_valid_name("p#unct"))
        self.assertFalse(actor.User.is_valid_name("punc\t"))
        self.assertFalse(actor.User.is_valid_name("punc\nn"))
        self.assertFalse(actor.User.is_valid_name("punc\\n"))
        self.assertFalse(actor.User.is_valid_name("@punct"))
        # space
        self.assertFalse(actor.User.is_valid_name("sp ace"))
