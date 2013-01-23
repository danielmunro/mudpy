from assign import Properties, Block, Attributes, Abilities

class Parser(object):
	IGNORE = ['definitions.mud']
	BASEPATH = 'scripts'

	def __init__(self, baseDir, fn):
		self.definitions = {}
		self.fp = None
		path = self.BASEPATH+'/'+baseDir
		self.parseFile(path+'/definitions.mud', 'parseDefinitions')
		self.parseDir(path, fn)
	
	def parseDir(self, path, fn):
		import os
		for infile in os.listdir(path):
			if not infile in self.IGNORE:
				fullpath = path+'/'+infile
				if os.path.isdir(fullpath):
					self.parseDir(fullpath, fn)
				elif fullpath.endswith('.mud'):
					self.parseFile(fullpath, fn)

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
		line = self.fp.readline()
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
		with open(scriptFile, 'r') as fp:
			self.fp = fp
			line = self.readline()
			while line:
				line = line.strip()
				if line:
					getattr(self, fn)(line)
				line = self.readline()
	
class ParserException(Exception): pass
