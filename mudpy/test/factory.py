import unittest
import json
from mudpy.mudpy.factory import Factory, FactoryException

class FooMock:
	def __init__(self):
		self.name = "0"
		self.level = 0
		self.type = ""
		self.hook = ""
		self.costs = {}
		self.messages = {}

class TestFactory(unittest.TestCase):

	def setUp(self):

		def getJsonStringWireframes():
			return """[{
			"FooMock":{
				"properties":{
					"name":"bar",
					"level":1,
					"type":"baz",
					"hook":"input",
					"costs":{
						"movement":1
					},
					"messages":{
						"success":{
							"invoker":"You wield foo with great power."
						},
						"fail":{
							"invoker":"Your foo power fails you."
						},
						"end":{
							"invoker":"You put foo away.",
							"*":"%s puts %s away."
						}
					}
				}
			}
		}]"""

		Factory.addWireframes(json.loads(getJsonStringWireframes()))

	def testAddWireframes(self):
		self.assertEquals(1, len(Factory.wireframes))
		self.assertIn("FooMock", Factory.wireframes.keys())

	def testNewWireframe(self):
		foo = Factory.newFromWireframe(FooMock="bar")
		self.assertIsInstance(foo, FooMock)
		self.assertEquals("bar", foo.name)
		self.assertEquals(1, foo.level)
		self.assertEquals("baz", foo.type)
		self.assertEquals("input", foo.hook)
		self.assertEquals("You wield foo with great power.", foo.messages["success"]["invoker"])
		self.assertEquals("Your foo power fails you.", foo.messages["fail"]["invoker"])
		self.assertEquals("You put foo away.", foo.messages["end"]["invoker"])
		self.assertEquals("%s puts %s away.", foo.messages["end"]["*"])
	
	def testWireframeDoesNotExist(self):
		def newClassDoesNotExist():
			return Factory.newFromWireframe(ClassDoesNotExist = 'classdoesnotexist')
		self.assertRaises(FactoryException, newClassDoesNotExist)
