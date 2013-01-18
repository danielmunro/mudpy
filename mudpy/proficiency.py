class Proficiency(object):
	name = ""
	improvementhook = ""
	improvementthreshold = 0.95
	level = 15
	observer = None

	def __init__(self, observer):
		self.observer = observer
		observer.attach(self.improvementhook, self)
	
	def getLevel(self):
		try:
			return self.level + self.observer.race.proficiencies[self.name]
		except KeyError:
			return self.level
	
	def checkimprove(self, subject, improvementthreshold):
		if improvementthreshold is None:
			improvementthreshold = self.improvementthreshold
		from random import random
		roll = random()
		if roll > self.improvementthreshold:
			self.level += 1
			return True
		return False
	
	def messageSuccess(self):
		return "Your skill in "+str(self)+" improves!\n"
	
	def messageLearnSuccess(self):
		return "Learning from your mistakes, your skill in "+str(self)+" improves!\n"
	
	def __str__(self):
		return self.name

class Melee(Proficiency):
	name = "melee"
	improvementhook = "attackresolution"

	def attackresolution(self, attack):
		if attack.success and self.checkimprove(attack.aggressor):
			attack.aggressor.notify(self.messageSuccess())

class HandToHand(Proficiency):
	name = "hand to hand"
	improvementhook = "attackresolution"

	def attackresolution(self, attack):
		if self.checkimprove(attack.aggressor, self.improvementthreshold - 0.03 if attack.success else self.improvementthreshold + 0.03):
			attack.aggressor.notify(self.messageSuccess() if attack.success else self.messageLearnSuccess())

class LightArmor(Proficiency):
	name = "light armor"
	improvementhook = "attacked"

	def attacked(self, attack):
		pass

class HeavyArmor(Proficiency):
	name = "heavy armor"
	improvementhook = "attacked"

	def attacked(self, attack):
		pass

class Parry(Proficiency):
	name = "parry"
	improvementhook = "attacked"

	def attacked(self, attack):
		pass

class Dodge(Proficiency):
	name = "dodge"
	improvementhook = "attacked"

	def attacked(self, attack):
		pass

class Slash(Proficiency):
	name = "slash"
	improvementhook = "attack"

	def attack(self, attack):
		pass

class Pierce(Proficiency):
	name = "pierce"
	improvementhook = "attack"

	def attack(self, attack):
		pass

class Bash(Proficiency):
	name = "bash"
	improvementhook = "attack"

	def attack(self, attack):
		pass

class Sneak(Proficiency):
	name = "sneak"
	improvementhook = "move"

	def move(self, attack):
		pass

class Haggle(Proficiency):
	name = "haggle"
	improvementhook = "sell"

	def sell(self, sale):
		pass

class Alchemy(Proficiency):
	name = "alchemy"
	improvementhook = "brew"

	def brew(self, brew):
		pass

class Curative(Proficiency):
	name = "curative"
	improvementhook = "cast"

	def cast(self, casting):
		pass

class Healing(Proficiency):
	name = "healing"
	improvementhook = "cast"

	def cast(self, casting):
		pass

class Maladictions(Proficiency):
	name = "maladictions"
	improvementhook = "cast"

	def cast(self, casting):
		pass

class Benedictions(Proficiency):
	name = "benedictions"
	improvementhook = "cast"

	def cast(self, casting):
		pass

class Sorcery(Proficiency):
	name = "sorcery"
	improvementhook = "cast"

	def cast(self, casting):
		pass

class Elemental(Proficiency):
	name = "elemental"
	improvementhook = "cast"

	def cast(self, casting):
		pass
