from twisted.internet.protocol import Factory, Protocol

from actor import User
from room import RoomFactory
from command import Command

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
		self.transport.loseConnection()
	
	def dataReceived(self, data):
		data = data.strip()
		if self.user:
			self.checkInput(data)
		else:
			self.login(data)
	
	def write(self, message):
		self.transport.write(message);
	
	def checkInput(self, input):
		Command(self.user, input)
		self.user.notify("\n"+self.user.prompt())
	
	def login(self, name):
		self.user = User(self, name)
		self.user.room = self.factory.roomFactory.DEFAULT_ROOM
		self.user.room.addActor(self.user)
		self.user.look()
		self.user.notify("\n"+self.user.prompt())
		self.factory.heartbeat.attach(self.user)

class ClientFactory(Factory):
	protocol = Client
	clients = []
	roomFactory = None
	heartbeat = None

	def __init__(self, heartbeat):
		self.roomFactory = RoomFactory()
		self.heartbeat = heartbeat
