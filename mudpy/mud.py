import os, yaml
from . import observer
from .wireframes import *

__SCRIPTS_DIR__ = "scripts"
__self__ = observer.Observer()

def load(path):

	with open(path, "r") as fp:
		return yaml.load(fp.read())

def safe_load(*path):
	
	path = list(path)
	path[-1] = path[-1] + ".yaml"
	try:
		return load(os.path.join(__SCRIPTS_DIR__, *path))
	except FileNotFoundError:
		pass

def run():

	from . import server

	print("running mud on port "+str(server.ThreadedTCPServer._port))
	server.start(__self__)