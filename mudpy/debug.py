class Debug:
	fp = None

	@staticmethod
	def log(message, status = "info"):
		if not Debug.fp:
			Debug.fp = open('debug.log', 'a')
			Debug.fp.write('\nnew log started\n')
		Debug.fp.write('['+status+'] '+message+'\n')
		Debug.fp.flush()
