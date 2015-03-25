import requests, json, copy

GTAA_ENDPOINT = "http://data.beeldengeluid.nl/gtaa/%s.json"
# IMMIX_ENDPOINT = "http://in.beeldengeluid.nl/collectie/api/search"
IMMIX_ENDPOINT = "http://labs.beeldengeluid.nl/mm/mm-basic/search"

"""
IMMIX_PAYLOAD = {
    "phrase": "",
    "page": "1",
    "numkeyframes": "1",
    "sorting": "SORT-DEF",
    "mediaType": "ALL_MEDIA",
    "pagesize": 12,
    "startdate": "",
    "enddate": "",
    "publiclyViewableResultsOnly": "true",
    "digitalViewableResultsOnly": None,
    "termFilters": {}
}
"""

IMMIX_PAYLOAD = {
    "zoekVraag": "*",
    "zoekInOndertitels": False,
    "pagina": 1,
    "paginaGrootte": 10,
    "sort": "TITLE_ASC",
    "facetFilters": [],
    "specificFields": [],
    "transcriptFields": []
}

def byperson(gtaa):
    gtaaurl = GTAA_ENDPOINT % gtaa
    r = requests.get(gtaaurl)
    prefLabel = r.json()['prefLabel'][0]

    payload = copy.deepcopy(IMMIX_PAYLOAD)
    # payload['termFilters']["Persoonsnamen"] = [ prefLabel ]

    payload['specificFields'].append({
        "operator": "and",
        "field": "personen",
        "value": prefLabel
    })


    headers = {
        'Content-Type' : 'application/json;charset=UTF-8',
        'User-Agent' : 'BengDB/1.0'
    }

    r = requests.post(IMMIX_ENDPOINT, data = json.dumps(payload), headers = headers)

    return r.json().get("searchResults", None)