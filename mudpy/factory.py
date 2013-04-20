class Factory:
	wireframes = {}

	@staticmethod
	def newFromWireframe(instance, name):
		try:
			wireframes = Factory.wireframes[instance.__class__.__name__][name]
		except KeyError:
			raise FactoryException("Factory does not know how to create "+name)
		from parser import Parser
		p = Parser()
		return p.buildFromDefinition(instance, wireframes[instance.__class__.__name__])

	@staticmethod
	def addWireframes(wireframes):
		for wireframe in wireframes:
			for key, blob in wireframe.iteritems():
				name = blob['properties']['name']
				try:
					Factory.wireframes[key][name] = wireframe
				except KeyError:
					Factory.wireframes[key] = {}
					Factory.wireframes[key][name] = wireframe
	
	@staticmethod
	def matchWireframe(name, keys, scalar = True):
		matches = []
		if not isinstance(keys, list):
			keys = [keys]
		for key in keys:
			for wireframename, wireframe in Factory.wireframes[key].iteritems():
				if wireframename.startswith(name):
					match = {'key':key, 'wireframe':wireframename}
					try:
						match['priority'] = wireframe['priority']
					except KeyError:
						match['priority'] = 0
					matches.append(match)
		import operator
		matches = sorted(matches, key=operator.itemgetter('priority'))
		try:
			return matches[0] if scalar else matches
		except IndexError:
			return None

class FactoryException(Exception): pass
