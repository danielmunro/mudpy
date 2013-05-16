import unittest, json
from mudpy.mudpy import factory

class FooMock:
	def __init__(self):
		self.name = ""
		self.level = 0
		self.type = ""
		self.hook = ""
		self.costs = {}
		self.messages = {}

class TestFactory(unittest.TestCase):

	def setUp(self):

		def getJsonStringWireframes():
			return """[{
			"mudpy.mudpy.test.factory.FooMock":{
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

		factory.add(json.loads(getJsonStringWireframes()))

	def testAddWireframes(self):
		self.assertEquals(1, len(factory.__wireframes__))
		self.assertIn("mudpy.mudpy.test.factory.FooMock", factory.__wireframes__.keys())

	def testNewWireframe(self):
		foo = factory.new(FooMock(), "bar")
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
			return factory.new(FooMock(), 'classdoesnotexist')
		self.assertRaises(factory.FactoryException, newClassDoesNotExist)
