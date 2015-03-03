from entity import WikidataEntity
from search import WikidataSearch
from query import WikidataQuery
from linkshere import WikidataLinkshere

CACHEABLE = True

methods = ("entity", "search", "query", "random", "labels", "linkshere")

def run(args, method):
    opts = {
        "q"             : args.get("q", False),
        "language"      : args.get("lang", "en"),
        "from"          : args.get("from", 0),
        "size"          : args.get("size", 10),
        "resolveimages" : args.get("resolveimages", True),
        "imagewidth"    : args.get("imagewidth", 300),
        "resolvedata"   : args.get("resolvedata", False)
    }

    if method == "random":
        entity = WikidataEntity()
        return entity.random(opts)

    if "q" not in args:
        raise Exception("No query given")

    if method == "linkshere":
        links = WikidataLinkshere(opts)
        return links.linkshere(opts["q"])

    if method == "labels":
        ids = opts["q"].split(",")

        entity = WikidataEntity()
        return entity.labels(ids, opts["language"])

    if method == "entity":
        entity = WikidataEntity()
        return entity.entity(opts)

    if method == "search":
        search = WikidataSearch()
        return search.search(opts)

    if method == "query":
        query = WikidataQuery()
        return query.query(opts)