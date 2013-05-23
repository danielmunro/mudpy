from mudpy import debug, observer
import time, os, pickle

__CALENDAR_DATA__ = os.path.join(os.getcwd(), 'servertime.pk')

def suffix(dec):
    return 'th' if 11<=dec<=13 else {1:'st',2:'nd',3:'rd'}.get(dec%10, 'th')

class Instance(observer.Observer):

    HOURS_IN_DAY = 24
    
    def __init__(self):
        super(Instance, self).__init__()
        self.elapsed_time = 0
        self.hour = 0
        self.day_of_month = 1
        self.month = 1
        self.year = 0

    def tick(self):
        self.elapsed_time += 1
        self.hour += 1
        if self.hour == self.config.months[self.month]['sunrise']:
            self.dispatch('sunrise', calendar=self, changed="The sun begins to rise.")
        elif self.hour == self.config.months[self.month]['sunset']:
            self.dispatch('sunset', calendar=self, changed="The sun begins to set.")
        if self.hour == self.config.hours_in_day:
            self.hour = 0
            self.day_of_month += 1
            if self.day_of_month > self.config.months[self.month]['days_in_month']:
                self.day_of_month = 0
                self.month += 1
                if self.month > len(self.config.months)-1:
                    self.month = 0
                    self.year += 1
        self.save()

    def save(self):
        observers = self.observers
        self.observers = None
        with open(__CALENDAR_DATA__, 'wb') as fp:
            pickle.dump(self, fp, pickle.HIGHEST_PROTOCOL)
        self.observers = observers

    def __str__(self):
        if self.hour < 13:
            hour = self.hour
            time = 'am'
        else:
            hour = self.hour-12
            time = 'pm'

        return "It is %i o'clock %s, the %i%s day of %s" % (hour, time, self.day_of_month, suffix(self.day_of_month), self.config.months[self.month]["name"])

    def setup_listeners_for(self, func):
        self.attach('sunrise', func)
        self.attach('sunset', func)

    def teardown_listeners_for(self, func):
        self.detach('sunrise', func)
        self.detach('sunset', func)
               

class Config:

    def __init__(self):
        self.days = []
        self.months = []
        self.hours_in_day = 0
        self.sunrise = 0
        self.sunset = 0

try:
    with open(__CALENDAR_DATA__, 'rb') as fp:
        __instance__ = pickle.load(fp)
        __instance__.observers = {}
    debug.log("resuming calendar")
except (IOError, EOFError):
    __instance__ = Instance()
    debug.log("starting new calendar")
