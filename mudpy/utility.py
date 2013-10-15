"""Standard issue utility functions. Checks for matches from input with
collections of objects that have a name attribute.

"""

def match_partial(needle, *haystack):
    """Calls checkMatch with the 'find' function, finds any matches in the
    collection names.

    """

    n = str(needle)

    return next((i for i in haystack if str(i).lower().find(n))
