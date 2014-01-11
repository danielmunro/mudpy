"""Entry point for mud.py framework. Creates an observer object, which serves
as a proxy between the other observers running in the game. Loads game areas.
Starts the server listening for connections.

"""
def setup_graceful_shutdown():
    """Default SIGQUIT behavior is to trigger a crash report, at least for OSX.
    Calling sys.exit() is a more 'graceful' shutdown, avoiding crash reports.
    This is useful for debugging the mud when forced shutdowns are necessary
    and common.

    """

    import signal, sys, os

    def sigquit_handler(*_args):
        sys.exit(os.EX_SOFTWARE)

    signal.signal(signal.SIGQUIT, sigquit_handler)

from mudpy.sys import wireframe, observer, server

# Main game observer
__mudpy__ = observer.Observer()

# Load game areas
wireframe.load_areas()

# Graceful game shutdown
setup_graceful_shutdown()

# Start the server listening
server.start(__mudpy__)
