import util, requests

API_ENDPOINT = "http://data.beeldengeluid.nl/api/"
SCHEME_ENDPOINT = "http://data.beeldengeluid.nl/gtaa/%s"
SCHEMES = (
    "GeografischeNamen",
    "Geografisch",
    "Namen",
    "Persoonsnamen",
    "OnderwerpenBenG",
    "Onderwerpen",
    "Maker",
    "Genre"
)

def _format_concept(concept):
    hiddenLabel = concept.get("hiddenLabel", [None])
    prefLabel = concept.get("prefLabel", [None])
    scheme = concept.get("inScheme", [None])
    id_ = concept.get("notation", [None])

    return {
        "label" : hiddenLabel[0] if hiddenLabel[0] else prefLabel[0],
        "hiddenLabel" : hiddenLabel[0],
        "prefLabel" : prefLabel[0],
        "uuid" : concept.get("uuid", None),
        "scheme" : scheme[0],
        "id" : id_[0],
        "deleted" : concept.get("deleted", None),
        "uri" : concept.get("uri", None),
        "tenant" : concept.get("tenant", None)
    }

def lookup(id_):
    url = SCHEME_ENDPOINT % id_ + ".json"
    print url
    req = requests.get(url)

    if req.status_code == 404:
        return False

    return _format_concept(req.json())

def findconcepts(q, inScheme = None):
    endpoint = API_ENDPOINT + "find-concepts"

    if inScheme:
        if not inScheme in SCHEMES:
            raise Exception("Unknown scheme")

        scheme = SCHEME_ENDPOINT % inScheme
        q += ' AND inScheme:"%s"' % scheme

    r = util.apirequest(endpoint, {
        "q" : q,
        "format" : "json"
    })

    if not "response" in r:
        return False

    if not "docs" in r["response"] or len(r["response"]["docs"]) == 0:
        return False

    return map(_format_concept, r["response"]["docs"])