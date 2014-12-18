import util, requests, xmltodict, urllib

RDF_ENDPOINT = "http://dnv-beng.mijnlieff.nl/index.php/Speciaal:RDFExporteren/%s"
RESOLVER_ENDPOINT = "http://dnv-beng.mijnlieff.nl/index.php/Speciaal:URIResolver/"

def _sanitize(string):
    string = string.replace(RESOLVER_ENDPOINT, "").replace("_", " ").replace("-", "%")
    string = urllib.unquote(string).encode('latin-1')
    return string

def _pluck(obj, node, key):
    if node not in obj:
        return False

    if isinstance(obj[node], dict):
        if key == "@rdf:resource":
            return _sanitize(obj[node][key])
        else:
            return obj[node][key]
    else:
        items = map(lambda i:i[key], obj[node])

        if key == "@rdf:resource":
            return map(_sanitize, items)
        else:
            return items

def _parse(item):
    # I <guess> the only useful stuff is in the first node, but then you might
    # never know!
    subject = item["rdf:RDF"]["swivt:Subject"][0]

    data = {
        "functions" : _pluck(subject, "property:HasFuncties", "#text"),
        "fullName" : _pluck(subject, "property:Has_FullName", "#text"),
        "birthDate" : _pluck(subject, "property:Has_Geboortedatum", "#text"),
        "birthPlace" : _pluck(subject, "property:Has_Geboorteplaats", "@rdf:resource"),
        "activePeriode" : _pluck(subject, "property:Has_PeriodeActief", "#text"),
        "activePeriodeEnd" : _pluck(subject, "property:Has_PeriodeActiefEind", "#text"),
        "activePeriodeStart" : _pluck(subject, "property:Has_PeriodeActiefStart", "#text"),
        "url" : _pluck(subject, "property:Has_URL", "@rdf:resource"),
        "knownFrom" : _pluck(subject, "property:IsBekendVan", "@rdf:resource"),
        "worksTogetherWith" : _pluck(subject, "property:WerktSamenMet", "@rdf:resource")
    }

    return data


def define(q, expanded = False):
    url = RDF_ENDPOINT % q
    req = requests.get(url)
    item = xmltodict.parse(req.text)

    if expanded:
        return item
    else:
        return _parse(item)