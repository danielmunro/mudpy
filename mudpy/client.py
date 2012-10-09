from twisted.internet.protocol import Factory as tFactory, Protocol
from collections import deque

from actor import User
from command import Command, MoveDirection
from ability import Ability
from room import Room
from utility import *
from factory import Factory

class Client(Protocol):
	def connectionMade(self):
		self.write("By what name do you wish to be known? ");
		self.factory.clients.append(self)
		self.user = None
		self.loginSteps = deque(["name", "race"])
	
	def connectionLost(self, reason):
		self.write("Good bye!")
		self.factory.clients.remove(self)
	
	def disconnect(self):
		self.factory.heartbeat.detach('tick', self.user)
		self.user.room.actors.remove(self.user)
		self.transport.loseConnection()
	
	def dataReceived(self, data):
		data = data.strip()
		if self.user:
			args = data.split(" ")
			action = startsWith(args[0], MoveDirection.__subclasses__(), Command.__subclasses__(), Ability.__subclasses__())
			if action:
				action().tryPerform(self.user, args)
			else:
				self.user.notify("What was that?")
			self.write("\n"+self.user.prompt())
		else:
			self.login(data)
	
	def write(self, message):
		self.transport.write(message);
	
	def login(self, data):
		next = self.loginSteps.popleft()
		if next == "name":
			self.newUser = User()
			self.newUser.client = self
			self.newUser.name = data
			self.write("What is your race? ")
			return
		elif next == "race":
			try:
				self.newUser.race = Factory.new(Race = data)
			except NameError:
				self.write("That is not a valid race. What is your race? ")
				self.loginSteps.appendleft(next)
				return
			self.user = self.newUser
			self.user.room = self.factory.DEFAULT_ROOM
			self.user.room.actors.append(self.user)
			Factory.new(Command = "look").tryPerform(self.user)
			self.write("\n"+self.user.prompt())

		from item import Item, Equipment 
		i = Item()
		i.name = 'an item'
		i.value = 10
		self.user.inventory.append(i)
		
		i = Equipment()
		i.name = 'a subissue sword'
		i.position = 'wield'
		i.value = 0
		i.attributes.hp = 1
		self.user.inventory.append(i)
		"""
		self.user.save()
		"""

class ClientFactory(tFactory):
	protocol = Client
	clients = []
	heartbeat = None
	DEFAULT_ROOM = None

	def __init__(self, heartbeat):
		self.heartbeat = heartbeat
		self.DEFAULT_ROOM = Room.rooms["midgaard:1"]
