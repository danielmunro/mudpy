from utility import matchPartial
from observer import Observer
from copy import copy

class Ability(Observer):
	instances = []
	def __init__(self):
		self.name = "an ability"
		self.level = 0
		self.affects = []
		self.costs = {}
		self.delay = 0
		self.type = "" # skill or spell
		self.hook = ""
		self.aggro = False
		self.messages = {}
		super(Ability, self).__init__()
	
	def tryPerform(self, invoker, args):
		try:
			receiver = matchPartial(args[-1], invoker.room.actors)
		except IndexError:
			receiver = invoker
		if self.applyCost(invoker):
			if self.rollsSuccess(invoker, receiver):
				self.perform(invoker, receiver, args)
			else:
				receiver.room.announce(self.getMessages('fail', invoker, receiver))
		else:
			invoker.notify("You do not have enough energy to do that.")

	def perform(self, invoker, receiver, args):

		receiver.room.announce(self.getMessages('success', invoker, receiver))

		self.dispatch(perform=self)

		def endAffect(ability):
			receiver.room.announce(self.getMessages('end', receiver))

		for affect in self.affects:
			a = copy(affect)
			a.attach('end', endAffect)
			a.start(receiver)

	def rollsSuccess(self, invoker, receiver):
		return True # chosen by coin toss, guaranteed to be random
	
	def getMessages(self, messagePart, invoker, receiver = None):
		messages = self.messages[messagePart]
		try:
			messages[invoker] = messages.pop('invoker')
			if messages[invoker].find('%s') > -1:
				messages[invoker] = messages[invoker] % str(receiver)
		except KeyError: pass
		try:
			messages[receiver] = messages.pop('receiver')
			if messages[receiver].find('%s') > -1:
				messages[receiver] = messages[receiver] % str(receiver)
		except KeyError: pass
		try:
			messages['*'] = messages.pop('*')
			if messages['*'].find('%s') > -1:
				messages['*'] = messages['*'] % str(invoker)
			if messages['*'].find('%s') > -1:
				messages['*'] = messages['*'] % str(receiver)
		except KeyError: pass
		return messages
	
	def applyCost(self, invoker):
		for attr, cost in self.costs.iteritems():
			curattr = getattr(invoker, 'cur'+attr)
			cost *= curattr if cost > 0 and cost < 1 else 1
			if curattr < cost:
				return False
		for attr, cost in self.costs.iteritems():
			curattr = getattr(invoker, 'cur'+attr)
			cost *= curattr if cost > 0 and cost < 1 else 1
			setattr(invoker, 'cur'+attr, curattr-cost)
		return True
	
	def __str__(self):
		return self.name;
