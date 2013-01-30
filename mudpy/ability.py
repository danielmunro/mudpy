from utility import *
from affect import Affect
from heartbeat import Heartbeat

class Ability(object):
	name = "an ability"
	level = 0
	affects = []
	costs = {}
	type = "" # skill or spell
	messageSuccess = ""
	messageFail = ""
	hook = ""

	def perform(self, invoker, args):
		receiver = matchPartial(args[-1], invoker.room.actors)
		if not receiver:
			receiver = invoker
		if self.applyCost(invoker) and self.rollsSuccess(invoker, receiver):
			self.announceSuccess(invoker, receiver)
			affects = self.getAffects(receiver)
			if affects:
				for affect in affects:
					affect.start()
		else:
			self.announceFail(invoker, receiver)

	def rollsSuccess(self, invoker, receiver):
		success = True

		return success
	
	def getAffects(self):
		return []

	def announceSuccess(self, invoker, receiver):
		pass

	def announceFail(self, invoker, receiver):
		pass
	
	def applyCost(self, invoker):
		for attr, cost in self.costs.iteritems():
			curattr = invoker.getAttribute(attr)
			cost *= curattr if cost > 0 and cost < 1 else 1
			if curattr < cost:
				return False
		for attr, cost in self.costs.iteritems():
			cost *= curattr if cost > 0 and cost < 1 else 1
			setattr(invoker.attributes, attr, curattr - cost)
		return True
	
	def __str__(self):
		return self.name;

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

