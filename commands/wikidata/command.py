from entity import WikidataEntity
from search import WikidataSearch
from query import WikidataQuery

CACHEABLE = True

methods = ("entity", "search", "query")

def run(args, method):
    if "q" not in args:
        raise Exception("No query given")

    opts = {
        "q" : args["q"],
        "language" : args.get("language", "en"),
        "from" : args.get("from", 0),
        "size" : args.get("size", 10),
        "resolveimages" : args.get("resolveimages", False),
        "imagewidth" : args.get("imagewidth", False),
        "imageheight" : args.get("imageheight" , False),
        "resolvedata" : args.get("resolvedata", False)
    }

    if method == "entity":
        entity = WikidataEntity()
        return entity.entity(opts)

    if method == "search":
        search = WikidataSearch()
        return search.search(opts)

    if method == "query":
        query = WikidataQuery()
        return query.query(opts)