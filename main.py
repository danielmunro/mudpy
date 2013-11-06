"""Entry point for mud.py. Set the scripts path from args, which wireframes,
and game data load from during initialization. Start event will instantiate the
server, calendar, and areas.

"""

from mudpy.sys import mudpy
import sys

def main(mudpy):
    mudpy.start()

if __name__ == "__main__":

    if len(sys.argv) > 1:
        __mudpy__ = mudpy.Mudpy(sys.argv[1])
    else:
        debug.error("Needs path, ie python main.py example")
        sys.exit()

    main(__mudpy__)
