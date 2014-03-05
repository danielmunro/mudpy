import os, yaml
from . import observer
from .wireframes import *

__scripts_dir__ = "scripts"
__self__ = observer.Observer()

def load(path):

	print("loading "+path)
	with open(path, "r") as fp:
		return yaml.load(fp.read())

def safe_load(*path):
	
	full_path = os.path.join(__scripts_dir__, *path)+".yaml"

	try:
		return load(full_path)
	except FileNotFoundError:
		pass

def run():

	from . import server

	print("running mud on port "+str(server.ThreadedTCPServer._port))
	server.start(__self__)