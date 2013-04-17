from time import strftime

class Debug:
	fp = None

	@staticmethod
	def log(message, status = "info"):
		if not Debug.fp:
			Debug.fp = open('debug.log', 'a')
			Debug.fp.write('\nnew log started\n')
		Debug.fp.write('['+strftime('%Y-%m-%d %H:%M:%S')+' '+str(status)+'] '+str(message)+'\n')
		Debug.fp.flush()

		# better error visibility
		if status == 'error':
			raise DebugException(message)

class DebugException(Exception): pass
