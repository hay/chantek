from entity import WikidataEntity
import util, json

API_ENDPOINT = "https://www.wikidata.org/w/api.php";

class WikidataLinkshere:
    def __init__(self, params):
        self.params = params

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

        links = r["query"]["pages"].itervalues().next().get("linkshere", None)

        if links:
            return [ i["title"] for i in links ]
        else:
            return False

    def linkshere(self, opts):
        results = self._linkshere(opts["q"])

        if not results:
            return False

        if self.params["resolvedata"]:
            entity = WikidataEntity()
            opts["q"] = ",".join(results)

            if self.params["resolvedata"] == "minimal":
                opts["props"] = ("labels", "descriptions")

            return entity.entity(opts)
        else:
            return results