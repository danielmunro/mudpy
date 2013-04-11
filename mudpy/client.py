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
import time

class Client(Protocol):
	def __init__(self):
		self.commandbuffer = []
		self.user = None
		self.login = Login(self)
		Heartbeat.instance.attach('cycle', self.processCommand)

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
	
	def processCommand(self):
		if self.user and self.user.delay_counter > 0:
			currenttime = int(time.time())
			if currenttime > self.user.last_delay:
				self.user.delay_counter -= 1
				self.user.last_delay = currenttime
			return

		try:
			data = self.commandbuffer.pop(0)
			if self.user:
				if data:
					args = data.split(" ")
					lookup = args.pop(0)
					action = startsWith(lookup, MoveDirection.__subclasses__(), Command.__subclasses__(), Ability.instances)
					if action:
						action.tryPerform(self.user, args)
						if isinstance(action, Ability):
							self.user.delay_counter += action.delay+1
					else:
						self.user.notify("What was that?")
				self.write("\n"+self.user.prompt())
			else:
				user = self.login.doStep(data)
				if isinstance(user, User):
					self.user = user
		except IndexError: pass
	
	def write(self, message):
		self.transport.write(str(message));
	
class Login:

	def __init__(self, client):
		self.todo = ['login', 'race', 'alignment']
		self.done = []
		self.client = client
		self.newuser = None
	
	def doStep(self, data):
		step = self.todo.pop(0)
		success = getattr(self, step)(data)
		if success:
			self.done.append(step)
		else:
			self.todo.insert(0, step)
		return success

	def login(self, data):
		user = Load.loadUser(data)
		if user:
			user.client = self.client
			Factory.new(Command = "look").tryPerform(user)
			user.notify("\n"+user.prompt())
			Debug.log('client logged in as '+str(user))
			return user
		self.newuser = User()
		self.newuser.client = self.client
		self.newuser.name = data
		self.newuser.notify("What is your race? ")
		return True
	
	def race(self, data):
		try:
			self.newuser.race = Factory.new(Race = data, newWith = self.newuser)
		except NameError:
			self.newuser.notify("That is not a valid race. What is your race? ")
			return False
		self.newuser.notify("What alignment are you (good/neutral/evil)? ")
		return True
	
	def alignment(self, data):
		if "good".find(data) == 0:
			self.newuser.alignment = 1000
		elif "neutral".find(data) == 0:
			self.newuser.alignment = 0
		elif "evil".find(data) == 0:
			self.newuser.alignment = -1000
		else:
			self.newuser.notify("That is not a valid alignment. What is your alignment? ")
			return False
		self.newuser.room = Room.rooms[Room.DEFAULTROOMID]
		self.newuser.room.actors.append(self.newuser)
		Factory.new(Command = "look").tryPerform(self.newuser)
		self.newuser.notify("\n"+self.newuser.prompt())
		Save.saveUser(self.newuser)
		Debug.log('client created new user as '+str(self.newuser))
		return self.newuser

class ClientFactory(tFactory):
	protocol = Client
	clients = []
