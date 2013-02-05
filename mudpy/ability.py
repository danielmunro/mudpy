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
			if not attr == "id" and not attr.startswith('max'):
				curattr = invoker.getAttribute(attr)
				cost *= curattr if cost > 0 and cost < 1 else 1
				if curattr < cost:
					return False
		for attr, cost in vars(self.costs).items():
			if not attr == "id" and not attr.startswith('max'):
				cost *= curattr if cost > 0 and cost < 1 else 1
				setattr(invoker.attributes, attr, curattr - cost)
		return True
	
	def __str__(self):
		return self.name;

"""
class Berserk(Ability):
	name = "berserk"
	level = 1
	costs = {'movement': .5}
	type = "skill"
	hook = "input"

	def announceSuccess(self, invoker, receiver):
		invoker.room.announce({
			invoker: "Your pulse speeds up as you are consumed by rage!",
			"*": str(invoker).title()+" goes into a rage!"
		})
	
	def announceFail(self, invoker, receiver):
		invoker.room.announce({
			invoker: "Your face gets red as you huff and puff.",
			"*": str(invoker).title()+" stomps around in a huff."
		})
		
	def getAffects(self, receiver):
		affect = Affect(receiver)
		affect.name = "berserk"
		affect.timeout = 2
		affect.wearOffMessage = "Your pulse slows down."
		affect.attributes.hp = round(receiver.getMaxAttribute('hp') * .1)
		affect.attributes.hit = round(receiver.getMaxAttribute('hit') * .1)
		affect.attributes.dam = round(receiver.getMaxAttribute('dam') * .1)
		return [affect]
"""

class Bash(Ability):
	name = "bash"
	level = 1
	type = "skill"
	hook = "input"

class SecondAttack(Ability):
	name = "second attack"
	level = 1
	type = "skill"
	hook = "melee"

class HandToHand(Ability):
	name = "hand to hand"
	level = 1
	type = "skill"
	hook = "melee"

class DirtKick(Ability):
	name = "dirt kick"
	level = 1
	type = "skill"
	hook = "input"

class Kick(Ability):
	name = "kick"
	level = 1
	type = "skill"
	hook = "input"
	messageSuccess = "Your kick %s %s."
	messageFail = "You kick wildly into the air."

"""
class Sneak(Ability):
	name = "sneak"
	level = 0
	type = "skill"
	hook = "input"
	messageSuccess = "You fade into the shadows."
	messageFail = "You fail to sneak silently."

	def getAffects(self, receiver):
		affect = Affect()
		affect.name = "sneak"
		affect.timeout = receiver.level
		affect.wearOffMessage = "You stop moving silently."
"""

class Infravision(Ability):
	name = "infravision"
	level = 0
	type = "skill"
	hook = "look"

class Heal(Ability):
	name = "heal"
	level = 1
	type = "spell"
	hook = "input"

