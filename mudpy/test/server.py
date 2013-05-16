import unittest, json
from mudpy.mudpy import server, factory

class TestServer(unittest.TestCase):

	def setUp(self):
		factory.add(json.loads("""[{
				"mudpy.mudpy.server.Instance":{
					"properties":{
						"port":9000,
						"name":"mud",
						"display_name":"My Great Mud"
					}
				}
			}]"""))

	def testImportInitializesHeartbeat(self):
		self.assertIsInstance(server.__instance__.heartbeat, server.Heartbeat)
	
	def testCreateMudInstance(self):
		instance = factory.new(server.Instance(), "mud")
		self.assertEquals(instance.port, 9000)
		self.assertEquals(instance.name, "mud")
		self.assertEquals(instance.display_name, "My Great Mud")
