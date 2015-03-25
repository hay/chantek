import util, requests, csv, os

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
    "Makers", # This is a hack, see the code below
    "Genre"
)

def _format_concept(concept):
    hiddenLabel = concept.get("hiddenLabel", [None])
    prefLabel = concept.get("prefLabel", [None])
    scheme = concept.get("inScheme", [None])
    id_ = concept.get("notation", [None])

    return {
        "label" : hiddenLabel if hiddenLabel else prefLabel,
        "hiddenLabel" : hiddenLabel,
        "prefLabel" : prefLabel,
        "uuid" : concept.get("uuid", None),
        "scheme" : scheme[0],
        "id" : id_[0],
        "deleted" : concept.get("deleted", None),
        "uri" : concept.get("uri", None),
        "tenant" : concept.get("tenant", None),
        "scopeNote" : concept.get("scopeNote", None)
    }

def lookupcombined(q, qtype):
    if qtype not in ("gtaa", "wikidata"):
        raise Exception("Invalid query type")

    csvfile = os.path.dirname(__file__) + "/combined.csv"

    for row in csv.DictReader(open(csvfile)):
        if row[qtype] == q:
            return row

    return False

def lookup(id_):
    url = SCHEME_ENDPOINT % id_ + ".json"
    req = requests.get(url)

    if req.status_code == 404:
        return False

    return _format_concept(req.json())

def findconcepts(q, inScheme = None):
    endpoint = API_ENDPOINT + "find-concepts"

    if inScheme:
        if not inScheme in SCHEMES:
            raise Exception("Unknown scheme")

        # Awful kludge, see below
        if inScheme == "Makers":
            realScheme = "Persoonsnamen"
        else:
            realScheme = inScheme

        scheme = SCHEME_ENDPOINT % realScheme
        q += ' AND inScheme:"%s"' % scheme

    r = util.apirequest(endpoint, {
        "q" : q,
        "format" : "json"
    })

    if not "response" in r:
        return False

    if not "docs" in r["response"] or len(r["response"]["docs"]) == 0:
        return False

    # "Makers" has been merged with "Persoonsnamen", so we need to use this
    # ugly kludge to get the actual maker
    if inScheme == "Makers":
        docs = []

        for d in r["response"]["docs"]:
            if "changeNote" not in d:
                continue

            if "Samengevoegd met: Maker" not in d["changeNote"][0]:
                continue

            docs.append(d)
    else:
        docs = r["response"]["docs"]

    return map(_format_concept, docs)