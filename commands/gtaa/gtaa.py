from operator import itemgetter
import util, requests, os, csv

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

def _combined_iterator():
    csvpath = os.path.dirname(__file__) + "/combined.csv"
    csvfile = open(csvpath)

    for row in csv.DictReader(csvfile):
        yield row

    csvfile.close()

def lookupcombined(q, qtype):
    if qtype not in ("gtaa", "wikidata", "bengwiki"):
        raise Exception("Invalid query type")

    for row in _combined_iterator():
        if row[qtype] == q:
            return row

    return False

def finditems(q, limit):
    return [r for r in _combined_iterator() if q.lower() in r["lookup"].lower() ][0:limit]

def listcombined():
    csvfile = os.path.dirname(__file__) + "/combined.csv"
    csvreader = csv.DictReader(open(csvfile))
    rows = []

    for row in csvreader:
        labels = row['label'].split(' - ')
        row['label'] = labels[0]

        try:
            row['labelsort'] = labels[1]
        except:
            row['labelsort'] = ""

        rows.append(row)

    return sorted(rows, key = itemgetter('labelsort'))

def lookup(id_):
    url = SCHEME_ENDPOINT % id_ + ".json"
    req = requests.get(url)

    if req.status_code == 404:
        return False

    return _format_concept(req.json())