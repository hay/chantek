from entity import WikidataEntity
from search import WikidataSearch
from query import WikidataQuery
from linkshere import WikidataLinkshere

methods = ("entity", "search", "query", "random", "labels", "linkshere")
CACHEABLE = ("entity", "search", "query", "labels", "linkshere") # 'Random' is not cacheable

def run(args, method):
    opts = {
        "q"              : args.get("q", False),
        "language"       : args.get("lang", "en"),
        "from"           : args.get("from", 0),
        "size"           : args.get("size", 10),
        "resolveimages"  : args.get("resolveimages", True),
        "imagewidth"     : args.get("imagewidth", 300),
        "resolvedata"    : args.get("resolvedata", False),
        "optionalclaims" : args.get("optionalclaims", True) # Should the item have claims? Only useful for the 'random' method really
    }

    if method == "random":
        entity = WikidataEntity()
        return entity.random(opts)

    if "q" not in args:
        raise Exception("No query given")

    if method == "linkshere":
        links = WikidataLinkshere(opts)
        return links.linkshere(opts)

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