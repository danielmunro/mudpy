import inspect

def matchPartial(needle, *haystack):
    return checkMatch(needle, 'find', haystack)

def checkMatch(needle, function, haystack):
    for h in haystack:
        for i in h:
            att = getattr(getattr(i, 'name').lower(), function)(needle)
            if not att is False and (att > -1 or att is True):
                return i() if inspect.isclass(i) else i
