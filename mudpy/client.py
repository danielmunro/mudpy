from twisted.internet.protocol import Factory as tFactory, Protocol

from command import Command, MoveDirection
from utility import startsWith
from debug import Debug
from heartbeat import Heartbeat
from persistence import *
from actor import User
from ability import Ability
from factory import Factory
from room import Room

from collections import deque

class Client(Protocol):
	def __init__(self):
		self.commandbuffer = []
		self.user = None
		self.login = Login(self)
		Heartbeat.instance.attach('cycle', self.poll)

	def connectionMade(self):
		self.write("By what name do you wish to be known? ");
		self.factory.clients.append(self)
		Debug.log('new client connected')
	
	def connectionLost(self, reason):
		self.write("Good bye!")
		self.factory.clients.remove(self)
		Debug.log('client disconnected')
	
	def disconnect(self):
		Heartbeat.instance.detach('tick', self.user)
		self.user.room.actors.remove(self.user)
		self.transport.loseConnection()
	
	def dataReceived(self, data):
		self.commandbuffer.append(data.strip())
	
	def poll(self):
		try:
			data = self.commandbuffer.pop(0)
		except IndexError:
			return

		if self.user:
			if data:
				args = data.split(" ")
				lookup = args.pop(0)
				action = startsWith(lookup, MoveDirection.__subclasses__(), Command.__subclasses__(), Ability.instances)
				if action:
					action.tryPerform(self.user, args)
				else:
					self.user.notify("What was that?")
			self.write("\n"+self.user.prompt())
		else:
			self.login.step(data)
	
	def write(self, message):
		self.transport.write(str(message));
	
class Login:

	def __init__(self, client):
		self.todo = ['login', 'race', 'alignment']
		self.done = []
		self.client = client
		self.newuser = None
	
	def step(self, data):
		def login(data):
			user = Load.loadUser(data)
			if user:
				user.client = self.client
				self.client.user = user
				user.loggedin()
				return
			self.newuser = User()
			self.newuser.client = self.client
			self.newuser.name = data
			self.client.write("What is your race? ")
		
		def race(data):
			try:
				self.newuser.race = Factory.new(Race = data, newWith = self.newuser)
			except NameError:
				raise LoginException("That is not a valid race. What is your race? ")
			self.client.write("What alignment are you (good/neutral/evil)? ")
		
		def alignment(data):
			if "good".find(data) == 0:
				self.newuser.alignment = 1000
			elif "neutral".find(data) == 0:
				self.newuser.alignment = 0
			elif "evil".find(data) == 0:
				self.newuser.alignment = -1000
			else:
				raise LoginException("That is not a valid alignment. What is your alignment? ")
			self.newuser.room = Room.rooms[Room.DEFAULTROOMID]
			self.newuser.room.actors.append(self.newuser)
			Save.saveUser(self.newuser)
			self.client.user = self.newuser
			Debug.log('client created new user as '+str(self.newuser))
			self.newuser.loggedin()

		step = self.todo.pop(0)

		try:
			locals()[step](data)
			self.done.append(step)
		except LoginException as e:
			self.client.write(e)
			self.todo.insert(0, step)

class ClientFactory(tFactory):
	protocol = Client
	clients = []

class LoginException(Exception): pass
