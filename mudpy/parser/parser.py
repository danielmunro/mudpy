import os
from assign import Properties, Block, Attributes, Abilities

class Parser(object):
	ignore = ['definitions']

	def __init__(self, baseDir):
		self.definitions = {}
		self.f = None
		self.parseDir("scripts/"+baseDir)
	
	def parseDir(self, path):
		if len(self.definitions) == 0:
			self.parseDefinitions(path)
		for infile in os.listdir(path):
			parts = infile.split(".")
			if not parts[0] in self.ignore:
				if len(parts) == 1:
					self.parseDir(path+"/"+parts[0])
				elif parts[1] == "mud":
					self.parseFile(path+"/"+parts[0]+".mud")
	
	def parseFile(self, fileName):
		raise ParserException('parseFile not defined')
	
	def readline(self, preserveReturn = True):
		line = self.f.readline()
		commentPos = line.find('#')
		if commentPos > -1:
			oline = line
			line = line[0:commentPos]
			if preserveReturn:
				line += oline[-1:]

		if not preserveReturn:
			line = line.strip()
		return line

	def parseDefinitions(self, path):
		with open(path+'/definitions.mud', 'r') as f:
			self.f = f
			line = self.readline()
			while line:
				defname = line.strip()
				if defname:
					self.definitions[defname] = []
					line = self.readcleanline()
					if not line:
						raise ParserException
					parts = line.split(',')
					for att in parts:
						ap = att.strip().split(' ', 1)
						if len(ap) == 1:
							self.definitions[defname].append(globals()[ap[0].title()]())
						else:
							self.definitions[defname].append(globals()[ap[0].title()](ap[1]))
				line = self.readline()
	
	def readcleanline(self):
		return self.readline(False)
	
class ParserException(Exception): pass
