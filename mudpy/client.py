from twisted.internet.protocol import Factory, Protocol
from collections import deque

from actor import User
from command import CommandFactory
from room import Room
from race import RaceFactory
from utility import *

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
		self.factory.heartbeat.detach(self.user)
		self.user.room.removeActor(self.user)
		self.transport.loseConnection()
	
	def dataReceived(self, data):
		data = data.strip()
		if self.user:
			args = data.split(" ")
			action = startsWith(args[0], CommandFactory.getCommands(), self.user.getAbilities())
			if action:
				action.perform(self.user, args)
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
				race = startsWith(data, RaceFactory.getRaces())
				if race:
					self.newUser.race = race
				else:
					raise Exception
			except Exception as e:
				self.write("That is not a valid race. What is your race? ")
				self.loginSteps.appendleft(next)
				return
			self.user = self.newUser
			self.user.room = self.factory.DEFAULT_ROOM
			self.user.room.appendActor(self.user)
			CommandFactory.getCommand("look").perform(self.user)
			self.write("\n"+self.user.prompt())
			self.factory.heartbeat.attach(self.user)

		from item import Item 
		import copy
		i1 = Item()
		i1.name = 'an item'
		i1.value = 10
		i2 = copy.copy(i1)
		self.user.inventory.append(i1)
		self.user.inventory.append(i2)
		"""
		self.user.save()
		"""

class ClientFactory(Factory):
	protocol = Client
	clients = []
	heartbeat = None
	DEFAULT_ROOM = None

	def __init__(self, heartbeat):
		self.heartbeat = heartbeat
		self.DEFAULT_ROOM = Room.rooms["midgaard:1"]
