"""Entry point for mud.py. Set the scripts path from args, which wireframes,
and game data load from during initialization. Start event will instantiate the
server, calendar, and areas.

"""

from mudpy import observer, debug
import sys

class Mudpy(observer.Observer):
    """Mudpy object is used to attach initialization and start events."""
    def __init__(self):
        self.observers = {}
        self.path = ""

__mudpy__ = Mudpy()

try:
    __mudpy__.path = sys.argv[1]
except KeyError:
    debug.log("Needs path, ie python main.py example", "error")
    raise

if __name__ == "__main__":
    from mudpy import wireframe, server, calendar, client, actor
    __mudpy__.dispatch('initialize')
    __mudpy__.dispatch('start')
