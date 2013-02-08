from utility import *
from affect import Affect
from attributes import Attributes
from heartbeat import Heartbeat
from copy import copy

class Ability(object):
	instances = []
	def __init__(self):
		self.name = "an ability"
		self.level = 0
		self.affects = []
		self.costs = Attributes()
		self.type = "" # skill or spell
		self.msgYouSuccess = ""
		self.msgYouFail = ""
		self.msgRoomSuccess = ""
		self.msgRoomFail = ""
		self.hook = ""

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
		if self.msgYouSuccess:
			receiver.notify(self.msgYouSuccess)
		if self.msgRoomSuccess:
			receiver.room.announce({
				receiver: None,
				'*': self.msgRoomSuccess
			})

	def announceFail(self, invoker, receiver):
		if self.msgYouFail:
			receiver.notify(self.msgYouFail)
		if self.msgRoomFail:
			receiver.room.announce({
				receiver: None,
				'*': self.msgRoomFail
			})
	
	def applyCost(self, invoker):
		for attr, cost in vars(self.costs).items():
			if not attr == "id" and cost != 0:
				curattr = invoker.getAttribute(attr)
				cost *= curattr if cost > 0 and cost < 1 else 1
				if curattr < cost:
					return False
		for attr, cost in vars(self.costs).items():
			if not attr == "id" and cost != 0:
				cost *= curattr if cost > 0 and cost < 1 else 1
				setattr(invoker.attributes, attr, curattr - cost)
		return True
	
	def __str__(self):
		return self.name;
