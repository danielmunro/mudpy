"""Helper function for dealing with collections of game objects."""

def find(needle, haystack):
    """Returns the first matching element from a list (using find). Casts 
    needle and list elements to string (and lower) to do a more fuzzy search.

    """

    n = str(needle).lower()

    return next((i for i in haystack if str(i).lower().find(n) == 0), None)
