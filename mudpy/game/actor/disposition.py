__standing__ = 'standing'
__sitting__ = 'sitting'
__laying__ = 'laying'
__sleeping__ = 'sleeping'
__incapacitated__ = 'incapacitated'

def get_regen_modifier(disposition):
    if disposition == __standing__ or disposition == __incapacitated__:
        return random.uniform(0.03, 0.08)
    elif disposition == __laying__ or disposition == __sitting__:
        return random.uniform(0.09, 0.15)
    elif diposition == __sleeping__:
        return random.uniform(0.16, 0.3)
