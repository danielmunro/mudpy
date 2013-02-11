class Proficiency(object):
	name = ""
	actionhook = ""
	improvementthreshold = 0.95
	level = 15
	observer = None

	def __init__(self, observer = None):
		if observer:
			self.observer = observer
			observer.attach(self.actionhook, self)
	
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
