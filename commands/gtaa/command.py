import gtaa

CACHEABLE = True

methods = ("findconcepts", "lookup", "lookupcombined", "listcombined")

def run(args, method):
    if method == "listcombined":
        return gtaa.listcombined()

    if "q" not in args:
        raise Exception("No query given")

    q = args["q"]

    if method == "findconcepts":
        return gtaa.findconcepts(q, inScheme = args.get("scheme", None))

    if method == "lookup":
        return gtaa.lookup(q)

    if method == "lookupcombined":
        qtype = args.get("type", "gtaa")
        return gtaa.lookupcombined(q, qtype)
