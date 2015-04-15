import gtaa

CACHEABLE = True

methods = ("finditems", "lookup", "lookupcombined", "listcombined")

def run(args, method):
    if method == "listcombined":
        return gtaa.listcombined()

    if "q" not in args:
        raise Exception("No query given")

    q = args["q"]
    limit = args.get("limit", 10)

    if method == "finditems":
        return gtaa.finditems(q, limit)

    if method == "lookup":
        return gtaa.lookup(q)

    if method == "lookupcombined":
        qtype = args.get("type", "gtaa")
        return gtaa.lookupcombined(q, qtype)
