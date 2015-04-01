import util, requests, xmltodict, urllib
from pyquery import PyQuery as pq
from commands.gtaa import gtaa

RDF_ENDPOINT = "http://dnv-beng.mijnlieff.nl/index.php/Speciaal:RDFExporteren/%s"
RESOLVER_ENDPOINT = "http://dnv-beng.mijnlieff.nl/index.php/Speciaal:URIResolver/"
WIKI_ENDPOINT = "http://beeldengeluidwiki.nl/api.php"

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

def _lookuphref(href):
    # This is a little ugly
    href = href.replace("/index.php/", "")

    if "action=edit" in href:
        return False

    lookup = gtaa.lookupcombined(href, "bengwiki")

    if lookup:
        return lookup["gtaa"]
    else:
        return False

def _parsehtml(html):
    d = pq(html)
    d.remove(".beeldengeluid-infobox")
    d.remove("#personen-foto")
    d.remove("#personen-gegevens")

    for a in d.find("a"):
        pa = pq(a)
        href = pa.attr("href")
        href = _lookuphref(href)
        text = pa.text()

        if href:
            pa.attr('href', href)
        else:
            # pa.insertAfter('<span>' + text + '</span>')
            pa.empty().prepend("<span>" + text + "</span>")

    # Check if there is still some html left
    if not d.html().strip():
        return False

    return d.html()

def pagetext(q):
    r = util.apirequest(WIKI_ENDPOINT, {
        "format"  : "json",
        "action"  : "query",
        "prop"    : "revisions",
        "titles"  : q,
        "rvprop"  : "content",
        "rvparse" : 1
    })

    if "-1" in r["query"]["pages"]:
        return False

    rev = r["query"]["pages"]
    rev = rev.itervalues().next()

    return _parsehtml(rev["revisions"][0]["*"])

def define(q, expanded = False):
    url = RDF_ENDPOINT % q
    req = requests.get(url)
    item = xmltodict.parse(req.text)

    if expanded:
        return item
    else:
        return _parse(item)