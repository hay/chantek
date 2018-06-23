from . import lookup

CACHEABLE = True
methods = ("define", "suggest")
arguments = {
    "limit" : 10,
    "q" : {
        "required" : True,
        "type" : str
    }
}

def run(args, method):
    if method == "define":
        return lookup.define(args)
    elif method == "suggest":
        return lookup.suggest(args)