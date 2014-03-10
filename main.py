from mudpy import observer, mud

if __name__ == "__main__":
	mud.__instance__ = observer.Observer()
	mud.run()