import os, yaml

__instance__ = None

def load(*path):
	
	full_path = os.path.join(__scripts_dir__, *path)+".yaml"
	
	with open(full_path, "r") as fp:
		return yaml.load(fp.read())

def safe_load(*path):
	
	try:
		return load(*path)
	except FileNotFoundError:
		pass

def run():

	from . import server

	print("running mud on port "+str(server.ThreadedTCPServer._port))
	__instance__.__rooms__ = load("rooms", "midgaard")
	server.start(__instance__)

__scripts_dir__ = "scripts"