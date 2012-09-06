from twisted.internet.protocol import Factory, Protocol

from actor import User
from command import Command
from room import Room

class Client(Protocol):
	def connectionMade(self):
		self.write("By what name do you wish to be known? ");
		self.factory.clients.append(self)
		self.user = None
	
	def connectionLost(self, reason):
		self.write("Good bye!")
		self.factory.clients.remove(self)
	
	def disconnect(self):
		self.factory.heartbeat.detach(self.user)
		self.user.room.removeActor(self.user)
		self.transport.loseConnection()
	
	def dataReceived(self, data):
		data = data.strip()
		if self.user:
			Command(self.user, data)
			self.user.notify("\n"+self.user.prompt())
		else:
			self.login(data)
	
	def write(self, message):
		self.transport.write(message);
	
	def login(self, name):
		self.user = User()
		self.user.client = self
		self.user.name = name
		self.user.room = self.factory.DEFAULT_ROOM
		self.user.room.appendActor(self.user)
		self.user.look()
		self.user.notify("\n"+self.user.prompt())
		self.factory.heartbeat.attach(self.user)
		self.user.save()

		from item import Item 
		import copy
		i1 = Item()
		i1.name = 'an item'
		i1.value = 10
		i2 = copy.copy(i1)
		self.user.inventory.append(i1)
		self.user.inventory.append(i2)

class ClientFactory(Factory):
	protocol = Client
	clients = []
	heartbeat = None
	DEFAULT_ROOM = None

	def __init__(self, heartbeat):
		self.heartbeat = heartbeat
		self.DEFAULT_ROOM = Room.rooms["midgaard:1"]
