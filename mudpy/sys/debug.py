"""Basic logger. Supports three levels of logging:

info - informational, messages go straight to the log file for tailing or
review later.

notice - probably not a good thing, but not fatal. Will output a message to
stdout as well as the log file.

error - this is an unrecoverable error. The message will be outputted to stdout
as well as the log file. Additionally, execution of the mud will come to a
halt.

"""

import time, os, sys

fp = None

if len(sys.argv) > 1:
    fp = open(os.path.join(sys.argv[1], 'data', 'debug.log'), 'a')
    fp.write('\nnew log started\n')

def log(message, status = "info"):
    """Log a message with the given status level."""

    if fp:
        fp.write('['+time.strftime('%Y-%m-%d %H:%M:%S')+' '+str(status)+'] '+ \
                                                             str(message)+'\n')
        fp.flush()

def notice(message):
    log(message, "notice")
    print message

def error(message):
    log(message, "error")
    print message
