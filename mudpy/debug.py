"""Basic logger. Supports three levels of logging:

info - informational, messages go straight to the log file for tailing or
review later.

notice - probably not a good thing, but not fatal. Will output a message to
stdout as well as the log file.

error - this is an unrecoverable error. The message will be outputted to stdout
as well as the log file. Additionally, execution of the mud will come to a
halt.

"""

import time

fp = open('debug.log', 'a')
fp.write('\nnew log started\n')

def log(message, status = "info"):
    """Log a message with the given status level."""

    # write the debug.log file
    fp.write('['+time.strftime('%Y-%m-%d %H:%M:%S')+' '+str(status)+'] '+ \
                                                         str(message)+'\n')
    fp.flush()

    # better error visibility and testing
    if status == 'error' or status == 'notice':
        print message

class DebugException(Exception):
    """Raised when an error message is passed to the debugger. Error messages
    do not kill execution (ie sys.exit()) for easier testability.

    """

    pass
