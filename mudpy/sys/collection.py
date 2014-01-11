"""Helper function for dealing with collections of game objects."""

def find(needle, haystack):
    """Returns the first matching element from a list (using find). Casts
    needle and list elements to string (and lower) to do a more fuzzy search.

    """

    return execute(needle, haystack, False)

def match(needle, haystack):
    return execute(needle, haystack, True)


def execute(needle, haystack, matching):

    n = str(needle).lower()

    if matching:
        return next((i for i in haystack if str(i).lower().find(n) > 0), None)
    else:
        return next((i for i in haystack if str(i).lower().find(n) == 0), None)