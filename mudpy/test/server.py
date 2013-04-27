import unittest, json
from mudpy.mudpy import server, heartbeat, factory

class TestServer(unittest.TestCase):

	def setUp(self):
		factory.add(json.loads("""[{
				"Instance":{
					"properties":{
						"port":9000,
						"name":"mud",
						"display_name":"My Great Mud"
					}
				}
			}]"""))

	def testImportInitializesHeartbeat(self):
		self.assertIsInstance(heartbeat.instance, heartbeat.Heartbeat)
	
	def testCreateMudInstance(self):
		instance = factory.new(server.Instance(), "mud")
		self.assertEquals(instance.port, 9000)
		self.assertEquals(instance.name, "mud")
		self.assertEquals(instance.display_name, "My Great Mud")
