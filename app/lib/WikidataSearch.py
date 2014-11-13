import util, json

API_ENDPOINT = "http://www.wikidata.org/w/api.php";

class WikidataSearch:
    def __init__(self):
        pass

    def search(self, params):
        r = util.apirequest(API_ENDPOINT, {
            "action" : "wbsearchentities",
            "format" : "json",
            "language" : params["language"],
            "type" : "item",
            "search" : params["q"]
        })

        if "success" in r:
            return r["search"]
        else:
            return False