wireframes = {}

def new(instance, name):
	global wireframes

	try:
		found = wireframes[instance.__class__.__name__][name]
	except KeyError:
		raise FactoryException("Factory does not know how to create "+name)
	from parser import Parser
	p = Parser()
	return p.buildFromDefinition(instance, found[instance.__class__.__name__])

def add(newwireframes):
	global wireframes

	for wireframe in newwireframes:
		for key, blob in wireframe.iteritems():
			name = blob['properties']['name']
			try:
				wireframes[key][name] = wireframe
			except KeyError:
				wireframes[key] = {}
				wireframes[key][name] = wireframe

def match(name, keys, scalar = True):
	global wireframes

	matches = []
	if not isinstance(keys, list):
		keys = [keys]
	for key in keys:
		for wireframename, wireframe in wireframes[key].iteritems():
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
