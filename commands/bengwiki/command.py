from . import bengwiki

CACHEABLE = True
methods = ("define", "pagetext")
arguments = {
    "expanded" : False,
    "q" : {
        "required" : True,
        "type" : str
    }
}

def run(args, method):
    if method == "define":
        return bengwiki.define(args["q"], expanded = args["expanded"])
    elif method == "pagetext":
        return bengwiki.pagetext(args["q"])