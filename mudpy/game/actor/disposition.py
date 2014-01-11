import random

__standing__ = 'standing'
__sitting__ = 'sitting'
__laying__ = 'laying'
__sleeping__ = 'sleeping'
__incapacitated__ = 'incapacitated'

def get_regen_modifier(disposition):
    if disposition == __standing__ or disposition == __incapacitated__:
        return random.uniform(0.07, 0.15)
    elif disposition == __laying__ or disposition == __sitting__:
        return random.uniform(0.16, 0.24)
    elif disposition == __sleeping__:
        return random.uniform(0.25, 0.4)
