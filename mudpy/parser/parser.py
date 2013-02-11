from assign import *
from mudpy.debug import Debug

class Parser(object):
	BASEPATH = 'mudpy/scripts'
	_globals = []

	def __init__(self, baseDir, fn):
		Debug.log('parsing scripts for '+baseDir)
		self.definitions = {}
		self.fp = None
		path = self.BASEPATH+'/'+baseDir
		self.parseFile(path+'/'+baseDir+'.definitions', self.parseDefinitions)
		self.parseDir(path, fn)

	def parseDefinitions(self, defname):
		defname = self.getclassfromline(defname);
		self.definitions[defname] = []
		line = self.readcleanline()
		Debug.log('adding definition for '+defname+': '+line)
		if not line:
			raise ParserException('a definition for '+defname+' was expected but not found')
		parts = line.split(',')
		for att in parts:
			ap = att.strip().split(' ', 1)
			if len(ap) == 1:
				self.definitions[defname].append(globals()[ap[0].title()]())
			else:
				self.definitions[defname].append(globals()[ap[0].title()](ap[1]))
	
	def parseDir(self, path, fn):
		import os
		for infile in os.listdir(path):
			fullpath = path+'/'+infile
			if os.path.isdir(fullpath):
				# recurse through scripts directory tree
				self.parseDir(fullpath, fn)
			elif fullpath.endswith('.mud'):
				# parse script
				self.parseFile(fullpath, fn)

	def parseFile(self, scriptFile, fn):
		Debug.log('parsing script file: '+scriptFile)
		with open(scriptFile, 'r') as fp:
			self.fp = fp
			line = self.readline()
			while line:
				_class = self.getclassfromline(line)
				if _class:
					fn(_class)
				line = self.readline()
	
	def applyDefinitionsTo(self, instance):
		try:
			for chunk in self.definitions[instance.__class__.__name__]:
				chunk.process(self, instance)
		except ParserException:
			pass
		Debug.log('[new '+instance.__class__.__name__+'] '+instance.name)
		return instance
	
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
		from proficiency import ProficiencyParser
		from affect import AffectParser
		from ability import AbilityParser
		from area import AreaParser
		from race import RaceParser
		for subclass in ['ProficiencyParser', 'AffectParser', 'AbilityParser', 'RaceParser', 'AreaParser']:
			locals()[subclass]().finishInitialization()

	def finishInitialization(self): pass
	
class ParserException(Exception): pass
