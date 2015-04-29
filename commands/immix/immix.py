import requests, json, copy, random

IMMIX_ENDPOINT = "http://in.beeldengeluid.nl/collectie/api/search"
MEDIA_ENDPOINT = "http://in.beeldengeluid.nl/collectie/%s"

IMMIX_PAYLOAD = {
    "numkeyframes": 1,
    "page" : 1,
    "mediaType": "IMAGE",
    "pagesize": 12,
    "publiclyViewableResultsOnly": "true",
    "termFilters": {
        "Persoonsnamen": []
    }
}

def imagesforperson(name):
    payload = copy.deepcopy(IMMIX_PAYLOAD)
    payload["termFilters"]["Persoonsnamen"].append(name)

    headers = {
        'Content-Type' : 'application/json;charset=UTF-8',
        'User-Agent' : 'BengDB/1.0'
    }

    r = requests.post(IMMIX_ENDPOINT, data = json.dumps(payload), headers = headers)

    items = r.json().get("responseItems", None)

    if not items:
        return None

    images = []

    # Nesting, baby!
    for hit in items:
        for positie in hit["posities"]:
            images.append({
                "label" : hit["mainTitle"],
                "expressie" : hit["expressie"]["id"],
                "thumb" : MEDIA_ENDPOINT % positie["thumbnailUri"].replace("./", ""),
                "image" : MEDIA_ENDPOINT % positie["consultancyCopyUri"].replace("./", "")
            })

    # A completely unscientific way to get 12 random images
    random.shuffle(images)
    return images[:12]