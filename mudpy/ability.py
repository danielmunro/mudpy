from utility import matchPartial
from observer import Observer
from reporter import Reporter
from copy import copy

class Ability(Observer, Reporter):
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
		from factory import Factory
		from affect import Affect

		self.dispatch(perform=self)

		for affectname in self.affects:
			Factory.newFromWireframe(Affect(), affectname).start(receiver)

	def rollsSuccess(self, invoker, receiver):
		return True # chosen by coin toss, guaranteed to be random
	
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
