from utility import *
from affect import Affect
from heartbeat import Heartbeat
from copy import copy

class Ability(object):
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
	
	def tryPerform(self, invoker, args):
		self.perform(invoker, args)

	def perform(self, invoker, args):
		try:
			receiver = matchPartial(args[-1], invoker.room.actors)
		except IndexError:
			receiver = invoker
		if self.applyCost(invoker):
			if self.rollsSuccess(invoker, receiver):
				self.announceSuccess(invoker, receiver)
				if self.affects:
					for affect in self.affects:
						a = copy(affect)
						a.affected = receiver
						a.start()
			else:
				self.announceFail(invoker, receiver)
		else:
			invoker.notify("You do not have enough energy to do that.")

	def rollsSuccess(self, invoker, receiver):
		success = True

		return success

	def announceSuccess(self, invoker, receiver):
		try:
			success = self.messages['self']['success']
		except KeyError:
			success = None
		try:
			roomSuccess = self.messages['room']['success']
		except KeyError:
			roomSuccess = None
		receiver.room.announce({
			receiver: success,
			'*': roomSuccess
		})

	def announceFail(self, invoker, receiver):
		try:
			fail = self.messages['self']['fail']
		except KeyError:
			success = None
		try:
			roomFail = self.messages['room']['fail']
		except KeyError:
			roomFail = None
		receiver.room.announce({
			receiver: fail,
			'*': roomFail
		})
	
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
