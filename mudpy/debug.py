import time

def log(message, status = "info"):
	# write the debug.log file
	fp = open('debug.log', 'a')
	fp.write('['+time.strftime('%Y-%m-%d %H:%M:%S')+' '+str(status)+'] '+str(message)+'\n')
	fp.close()

	# better error visibility
	if status == 'error':
		raise DebugException(message)

class DebugException(Exception): pass
