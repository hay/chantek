import util, json
from WikidataEntity import WikidataEntity

API_ENDPOINT = "http://wdq.wmflabs.org/api";

class WikidataQuery:
    def __init__(self):
        pass

    def query(self, params):
        r = util.apirequest(API_ENDPOINT, {
            "q" : params["q"]
        })

        status = r["status"]

        if r["status"]["error"] == "OK":
            frm, to = int(params["from"]), int(params["from"]) + int(params["size"])
            items = r["items"][frm:to]

            if params["resolvedata"] != False:
                entity = WikidataEntity()
                ids = ",".join(map(str, items))

                entities = entity.entity({
                    "q" : ids,
                    "language" : params["language"]
                })

                return entities
            else:
                return items
        else:
            return False