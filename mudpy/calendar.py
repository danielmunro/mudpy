"""Game calendar. Doesn't do much at this point except keep track of time."""

from . import wireframe

__config__ = None
__instance__ = None

def suffix(dec):
    """Helper function to get the suffix for a number, ie 1st, 2nd, 3rd."""

    return 'th' if 11 <= dec <= 13 else {
            1: 'st',2: 'nd',3: 'rd'}.get(dec%10, 'th')

def load(server):
    global __instance__
    try:
        __instance__ = wireframe.create("calendar", "data")
    except wireframe.WireframeException:
        __instance__ = Instance()
    server.__instance__.heartbeat.attach('tick', __instance__.tick)

class Instance(wireframe.Blueprint):
    """Calendar instance, keeps track of the date in the game."""

    yaml_tag = "u!calendar"

    def __init__(self):
        self.elapsed_time = 0
        self.hour = 0
        self.day_of_month = 1
        self.month = 1
        self.year = 0
        self.daylight = True
        self.observers = {}

    def tick(self):
        """Tick event listener function, increments the hour and checks for
        changes in the date.

        """

        self.elapsed_time += 1
        self.hour += 1
        if self.hour == __config__.months[self.month]['sunrise']:
            self.dispatch('sunrise', 
                    calendar=self, 
                    changed="The sun begins to rise.")
            self.daylight = True
        elif self.hour == __config__.months[self.month]['sunset']:
            self.dispatch('sunset', 
                    calendar=self, 
                    changed="The sun begins to set.")
            self.daylight = False
        if self.hour == __config__.hours_in_day:
            self.hour = 0
            self.day_of_month += 1
            if self.day_of_month > __config__.months[self.month]['days_in_month']:
                self.day_of_month = 1
                self.month += 1
                if self.month > len(__config__.months)-1:
                    self.month = 1
                    self.year += 1
        wireframe.save(self, "data")

    def get_game_time(self):
        if self.hour < 13:
            hour = self.hour
            time = 'am'
        else:
            hour = self.hour-12
            time = 'pm'

        return "It is %i o'clock %s, the %i%s day of %s, year %i" % (
                hour, time, self.day_of_month, suffix(self.day_of_month), 
                __config__.months[self.month]["name"], self.year)

    def __str__(self):
        return "calendar"

    def setup_listeners_for(self, func):
        """Binds function to calendar related events."""
        self.attach('sunrise', func)
        self.attach('sunset', func)

    def teardown_listeners_for(self, func):
        """Removes function from calendar related events."""
        self.detach('sunrise', func)
        self.detach('sunset', func)
