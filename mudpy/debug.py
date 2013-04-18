import time

fp = open('debug.log', 'a')
fp.write('\nnew log started\n')

def log(message, status = "info"):

	global fp

	# write the debug.log file
	fp.write('['+time.strftime('%Y-%m-%d %H:%M:%S')+' '+str(status)+'] '+str(message)+'\n')
	fp.flush()

	# better error visibility and testing
	if status == 'error':
		raise DebugException(message)

class DebugException(Exception): pass
