from twisted.internet.protocol import Factory as tFactory, Protocol

import command, debug, persistence, heartbeat, actor
from factory import Factory, FactoryException
from room import Room
from observer import Observer

from collections import deque

class Client(Observer, Protocol):
	def __init__(self):
		self.commandbuffer = []
		self.user = None
		self.login = Login(self)
		heartbeat.instance.attach('cycle', self.poll)
		super(Client, self).__init__()

	def connectionMade(self):
		self.write("By what name do you wish to be known? ");
		debug.log('new client connected')
	
	def connectionLost(self, reason):
		self.write("Good bye!")
		debug.log('client disconnected')
	
	def disconnect(self):
		heartbeat.instance.detach('tick', self.user)
		self.user.room.actors.remove(self.user)
		self.transport.loseConnection()
	
	def dataReceived(self, data):
		self.commandbuffer.append(data.strip())
	
	def poll(self):
		try:
			data = self.commandbuffer.pop(0)
		except IndexError:
			return
	
		if not self.user:
			return self.login.step(data)
		elif data:
			args = data.split(" ")
			args.insert(0, self.user)
			handled = self.dispatch(input=args)
			if not handled:
				self.user.notify("What was that?")

		self.write("\n"+self.user.prompt())
	
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
			user = persistence.loadUser(data)
			if user:
				user.client = self.client
				self.client.user = user
				user.loggedin()
				return
			self.newuser = actor.User()
			self.newuser.client = self.client
			self.newuser.name = data
			self.client.write("What is your race? ")
		
		def race(data):
			try:
				self.newuser.race = Factory.newFromWireframe(actor.Race(), data)
			except FactoryException:
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
			persistence.saveUser(self.newuser)
			self.client.user = self.newuser
			debug.log('client created new user as '+str(self.newuser))
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

	def buildProtocol(self, addr):
		client = Client()
		client.attach('input', command.checkInput)
		return client

class LoginException(Exception): pass
