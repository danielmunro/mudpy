"""Entry point for mud.py. Set the scripts path from args, which wireframes,
and game data load from during initialization. Start event will instantiate the
server, calendar, and areas.

"""

import sys
from mudpy.sys import wireframe, debug, mudpy

if len(sys.argv) > 1:
    wireframe.__path__ = sys.argv[1]
    wireframe.preload()
else:
    debug.error("Needs path, ie python main.py example")
    sys.exit()

def main(m):
    m.start()

__mudpy__ = mudpy.Mudpy()

if __name__ == "__main__":
    main(__mudpy__)
