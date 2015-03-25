import gtaa

methods = ("findconcepts", "lookup", "lookupcombined")

def run(args, method):
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
