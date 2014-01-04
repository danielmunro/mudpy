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

__fp__ = None
__env__ = None

args_len = len(sys.argv)
if args_len > 1:
    __fp__ = open(os.path.join(sys.argv[1], 'data', 'debug.log'), 'a')
    __fp__.write('\nnew log started\n')

    if args_len == 3:
        __env__ = sys.argv[2]

def log(message, status = "info"):
    """Log a message with the given status level."""

    if __fp__:
        __fp__.write('['+time.strftime('%Y-%m-%d %H:%M:%S')+' '+str(status)+'] '+ \
                                                             str(message)+'\n')
        __fp__.flush()

        if __env__ == "dev":
            print "["+status+"] "+message

def info(message):
    log(message, "info")

def notice(message):
    log(message, "notice")

def error(message):
    log(message, "error")
