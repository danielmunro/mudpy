from twisted.internet.protocol import Factory as tFactory, Protocol
from collections import deque

from command import Command, MoveDirection
from utility import *

class Client(Protocol):
	def connectionMade(self):
		self.write("By what name do you wish to be known? ");
		self.factory.clients.append(self)
		self.user = None
		self.loginSteps = deque(["login", "name", "race", "alignment"])
	
	def connectionLost(self, reason):
		self.write("Good bye!")
		self.factory.clients.remove(self)
	
	def disconnect(self):
		self.factory.heartbeat.detach('tick', self.user)
		self.user.room.actors.remove(self.user)
		self.transport.loseConnection()
	
	def dataReceived(self, data):
		from ability import Ability
		data = data.strip()
		if self.user:
			args = data.split(" ")
			action = startsWith(args[0], MoveDirection.__subclasses__(), Command.__subclasses__(), Ability.__subclasses__())
			if action:
				args.pop(0)
				action().tryPerform(self.user, args)
			else:
				self.user.notify("What was that?")
			self.write("\n"+self.user.prompt())
		else:
			self.login(data)
	
	def write(self, message):
		self.transport.write(message);
	
	def login(self, data):
		from factory import Factory
		next = self.loginSteps.popleft()
		if next == "login":
			from load import Load
			self.user = Load.loadUser(data)
			#self.user = None
			if self.user:
				self.user.client = self
				Factory.new(Command = "look").tryPerform(self.user)
				self.loginSteps = deque([])
			else:
				next = self.loginSteps.popleft()
		if next == "name":
			from actor import User
			self.newUser = User()
			self.newUser.client = self
			self.newUser.name = data
			self.write("What is your race? ")
			return
		elif next == "race":
			try:
				self.newUser.race = Factory.new(Race = data, newWith = self.newUser)
			except NameError:
				self.write("That is not a valid race. What is your race? ")
				self.loginSteps.appendleft(next)
				return
			self.write("What alignment are you (good/neutral/evil)? ")
		elif next == "alignment":
			if "good".find(data) == 0:
				self.newUser.alignment = 1000
			elif "neutral".find(data) == 0:
				self.newUser.alignment = 0
			elif "evil".find(data) == 0:
				self.newUser.alignment = -1000
			else:
				self.write("That is not a valid alignment. What is your alignment? ")
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
			i.weight = .3
			self.user.inventory.append(i)
			
			i = Equipment()
			i.name = 'a subissue sword'
			i.position = 'wield'
			i.value = 0
			i.attributes.hp = 1
			i.weight = 1
			self.user.inventory.append(i)
			from save import Save
			Save.saveUser(self.user)

class ClientFactory(tFactory):
	protocol = Client
	clients = []
	heartbeat = None
	DEFAULT_ROOM = None

	def __init__(self, heartbeat):
		from room import Room
		self.heartbeat = heartbeat
		self.DEFAULT_ROOM = Room.rooms["midgaard:1"]
