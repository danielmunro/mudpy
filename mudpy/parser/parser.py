from assign import *

class Parser(object):
	IGNORE = ['definitions.mud']
	BASEPATH = 'mudpy/scripts'
	_globals = []

	def __init__(self, baseDir, fn):
		self.definitions = {}
		self.fp = None
		path = self.BASEPATH+'/'+baseDir
		self.parseFile(path+'/definitions.mud', 'parseDefinitions', False)
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
		defname = self.getclassfromline(defname);
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

	def parseFile(self, scriptFile, fn, enforceDefinitions = True):
		with open(scriptFile, 'r') as fp:
			self.fp = fp
			line = self.readline()
			while line:
				line = self.getclassfromline(line)
				if line:
					if enforceDefinitions and not line in self.definitions:
						print '[error] "'+line+'" is not a parser definition'
					else:
						getattr(self, fn)(line)
				line = self.readline()
	
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

	@staticmethod
	def getclassfromline(line):
		return line.strip().title()

	@staticmethod
	def initializeParsers():
		from area import AreaParser
		from race import RaceParser
		for subclass in ['RaceParser', 'AreaParser']:
			locals()[subclass]().finishInitialization()

	def finishInitialization(self): pass
	
class ParserException(Exception): pass
