from .entity import WikidataEntity
from .search import WikidataSearch
from .query import WikidataQuery
from .linkshere import WikidataLinkshere

Q_METHODS = ["entity", "search", "query", "labels", "linkshere"]
methods = Q_METHODS + ["random"]
arguments = {
    "q" : {
        "required" : Q_METHODS,
        "type" : str
    },
    "language" : "en",
    "from" : 0,
    "size" : 10,
    "resolveimages" : True,
    "imagewidth" : 300,
    "resolvedata" : False,
    "optionalclaims" : True # Should the item have claims? Only useful for the 'random' method really
}
CACHEABLE = Q_METHODS

def run(args, method):
    if method == "random":
        entity = WikidataEntity()
        return entity.random(args)
    elif method == "linkshere":
        links = WikidataLinkshere(args)
        return links.linkshere(args)
    elif method == "labels":
        ids = args["q"].split(",")
        entity = WikidataEntity()
        return entity.labels(ids, args["language"])
    elif method == "entity":
        entity = WikidataEntity()
        return entity.entity(args)
    elif method == "search":
        search = WikidataSearch()
        return search.search(args)
    elif method == "query":
        query = WikidataQuery()
        return query.query(args)