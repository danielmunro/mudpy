import os
from assign import Properties, Block, Attributes, Abilities

class Parser(object):
	ignore = ['definitions']

	def __init__(self, baseDir, fn):
		self.definitions = {}
		self.f = None
		self.parseDir("scripts/"+baseDir, fn)
	
	def parseDir(self, path, fn):
		if len(self.definitions) == 0:
			self.parseFile(path+'/definitions.mud', 'parseDefinitions')
		for infile in os.listdir(path):
			parts = infile.split(".")
			if not parts[0] in self.ignore:
				if len(parts) == 1:
					self.parseDir(path+"/"+parts[0], fn)
				elif parts[1] == "mud":
					self.parseFile(path+"/"+parts[0]+".mud", fn)

	def parseDefinitions(self, defname):
		self.definitions[defname] = []
		line = self.readcleanline()
		if not line:
			raise ParserException("a definition for "+defname+" was expected but not found")
		parts = line.split(',')
		for att in parts:
			ap = att.strip().split(' ', 1)
			if len(ap) == 1:
				self.definitions[defname].append(globals()[ap[0].title()]())
			else:
				self.definitions[defname].append(globals()[ap[0].title()](ap[1]))
	
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
	
	def readcleanline(self):
		return self.readline(False)

	def parseFile(self, scriptFile, fn):
		with open(scriptFile, 'r') as f:
			self.f = f
			line = self.readline()
			while line:
				line = line.strip()
				if line:
					getattr(self, fn)(line)
				line = self.readline()
	
class ParserException(Exception): pass
