"""Entry point for mud.py. Set the scripts path from args, which wireframes,
and game data load from during initialization. Start event will instantiate the
server, calendar, and areas.

"""

from mudpy import mudpy, debug
import sys

def main():
    from mudpy import wireframe, server, calendar, client, actor
    __mudpy__.dispatch("initialize")
    __mudpy__.dispatch("start")

__mudpy__ = mudpy.Mudpy()

if __name__ == "__main__":

    # if mudpy is run directly, it needs a path from cli args to load the game
    if len(sys.argv) > 1:
        __mudpy__.path = sys.argv[1]
    else:
        debug.error("Needs path, ie python main.py example")
        sys.exit()

    main()
