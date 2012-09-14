from utility import *
from affect import Affect
from heartbeat import Heartbeat

class AbilityFactory:
	@staticmethod
	def newAbility(name):
		ability = startsWith(name, Ability.__subclasses__());
		return ability() if ability else None

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
		self.rollsSuccess(invoker, receiver)

	def rollsSuccess(self, invoker, receiver):
		success = True

		if success and self.messageSuccess:
			invoker.notify(self.messageSuccess+"\n")
			affects = self.getAffects(receiver)
			if affects:
				for affect in affects:
					affect.start()
		elif not success and self.messageFail:
			invoker.notify(self.messageFail+"\n")

		return success
	
	def getAffects(self):
		return []
	
	def __str__(self):
		return self.name;

class Berserk(Ability):
	name = "berserk"
	level = 1
	costs = {'movement': .5}
	type = "skill"
	messageSuccess = "Your pulse speeds up as you are consumed by rage!"
	messageFail = "Your face gets red as you huff and puff."
	hook = "input"
		
	def getAffects(self, receiver):
		affect = Affect(receiver)
		affect.name = "berserk"
		affect.timeout = 2
		affect.wearOffMessage = "Your pulse slows down."
		affect.attributes.hp = round(receiver.max_attributes.hp * .1)
		affect.attributes.hit = round(receiver.max_attributes.hit * .1)
		affect.attributes.dam = round(receiver.max_attributes.dam * .1)
		return [affect]

class SecondAttack(Ability):
	name = "second attack"
	level = 1
	type = "skill"
	hook = "melee"

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
