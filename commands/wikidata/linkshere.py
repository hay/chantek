import util, json

API_ENDPOINT = "http://www.wikidata.org/w/api.php";

class WikidataLinkshere:
    def __init__(self, params):
        self.params = params

    # Should probably be deployed to entity.py
    def _entities(self, ids):
        opts = {
            "action"           : "wbgetentities",
            "ids"              : "|".join(ids),
            "languages"        : self.params["language"],
            "format"           : "json",
            "languagefallback" : 1
        }

        r = util.apirequest(API_ENDPOINT, opts)

        return r

    def _linkshere(self, q):
        r = util.apirequest(API_ENDPOINT, {
            "action"      : "query",
            "prop"        : "linkshere",
            "titles"      : q,
            "lhnamespace" : 0,
            "lhshow"      : "!redirect",
            "format"      : "json",
            "lhlimit"     : 50
        })

        if "-1" in r["query"]["pages"]:
            return False

        links = r["query"]["pages"].itervalues().next()["linkshere"]

        return [ i["title"] for i in links ]

    def linkshere(self, q):
        results = self._linkshere(q)

        if not self.params["resolvedata"]:
            return results

        return self._entities(results)