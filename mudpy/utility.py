"""Standard issue utility functions. Checks for matches from input with
collections of objects that have a name attribute.

"""

import inspect

def match_partial(needle, *haystack):
    """Calls checkMatch with the 'find' function, finds any matches in the
    collection names.

    """

    return check_match(needle, 'find', haystack)

def check_match(needle, function, haystack):
    """checkMatch maps a string function to the name properties of a collection
    of objects and return any matches.

    """

    for h in haystack:
        for i in h:
            att = getattr(getattr(i, 'name').lower(), function)(needle)
            if not att is False and (att > -1 or att is True):
                return i() if inspect.isclass(i) else i
