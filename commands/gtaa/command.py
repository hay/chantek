from . import gtaa

CACHEABLE = True
methods = ("finditems", "lookup", "lookupcombined", "listcombined")
arguments = {
    "q" : {
        "required" : ["finditems", "lookup", "lookupcombined"],
        "type" : str
    },
    "limit" : 10,
    "type" : "gtaa"
}

def run(args, method):
    if method == "listcombined":
        return gtaa.listcombined()
    elif method == "finditems":
        return gtaa.finditems(args["q"], args["limit"])
    elif method == "lookup":
        return gtaa.lookup(args["q"])
    elif method == "lookupcombined":
        return gtaa.lookupcombined(args["q"], args["type"])