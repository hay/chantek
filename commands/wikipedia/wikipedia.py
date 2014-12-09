import requests, json, re, time

API_ENDPOINT = "http://%s.wikipedia.org/w/api.php";
RESIZE_ENDPOINT = "http://commons.wikimedia.org/wiki/Special:Redirect/file/%s?width=%s"

def request(lang, params):
    url = API_ENDPOINT % lang
    params.update({ "format" : "json" })
    r = requests.get(url, params = params)

    data = r.json()

    return data

def _getfirstpage(data):
    if "-1" in data["query"]["pages"]:
        return False

    # Sigh.. awful Wikipedia API crap
    pageid = data['query']['pages'].keys()[0]
    return data["query"]["pages"][pageid]

def _extracts(q, lang, intro = True):
    opts = {
        "action" : "query",
        "prop" : "extracts",
        "titles" : q
    }

    if intro:
        opts["exintro"] = 1

    data = request(lang, opts)

    page = _getfirstpage(data)

    if not page:
        return False

    if intro:
        # A bit ugly, but oh well
        page['extract'] = re.sub('<[^<]+?>', '', page['extract']).strip()

    return page

def imgresize(q, lang, imgwidth):
    # We got to remove the Namespace prefix, in all languages :/
    if ":" in q:
        parts = q.split(":")
        q = parts[1]

    return RESIZE_ENDPOINT % (q, imgwidth)

def article(q, lang, imgwidth):
    text = _extracts(q, lang, False)

    if not text:
        return False

    text = text["extract"]
    images = articleimages(q, lang)
    images = imageinfo(images, lang)

    # Remove all 'local' images, we can't redirect those to Commons
    images = filter(lambda i:i["imagerepository"] == "shared", images)

    for img in images:
        img["thumb"] = imgresize(img["title"], lang, imgwidth)

    return {
        "text" : text,
        "thumbnail" : thumbnail(q, lang, imgwidth),
        "images" : images
    }

def _imageinfo_format(img):
    if "imageinfo" not in img:
        return False

    info = img["imageinfo"][0]

    info.update({
        "imagerepository" : img["imagerepository"],
        "title" : img["title"]
    })

    return info

def thumbnail(q, lang, imgwidth):
    data = request(lang, {
        "action" : "query",
        "prop" : "pageimages",
        "titles" : q,
        "pithumbsize" : imgwidth
    })

    data = _getfirstpage(data)

    if not data:
        return False

    # Consistentcy, people!
    data["thumbnail"]["url"] = data["thumbnail"]["source"]

    return data["thumbnail"]

def imageinfo(images, lang):
    data = request(lang, {
        "action" : "query",
        "prop" : "imageinfo",
        "titles" : "|".join(images),
        "iiprop" : "url"
    })

    return map(_imageinfo_format, data["query"]["pages"].values())

def articleimages(q, lang):
    data = request(lang, {
        "action" : "query",
        "prop" : "images",
        "titles" : q
    })

    page = _getfirstpage(data)

    if not page:
        return False

    return map(lambda x:x["title"], page["images"])

def define(q, lang):
    return _extracts(q, lang, True)

def suggest(q, lang):
    data = request(lang, {
        "action" : "opensearch",
        "search" : q,
        "suggest" : 1
    });

    return {
        "query" : q,
        "suggestions" : data[1]
    }

# Right now, this only returns last month
def pageviews(q, lang):
    url = "http://stats.grok.se/json/%s/%s/%s" % (
        lang,
        "latest30",
        q
    )

    r = requests.get(url)
    stats = r.json()

    total = 0
    for (key, view) in stats["daily_views"].iteritems():
        total = total + int(view)

    stats["total"] = total

    return stats

def linkshere(q, lang):
    data = request(lang, {
        "action" : "query",
        "prop" : "linkshere",
        "titles" : q,
        "lhlimit" : 500
    })

    data = data["query"]["pages"].values()[0]

    if "linkshere" in data:
        data["total"] = len(data["linkshere"])
    else:
        data["total"] = 0

    return data

def langlinks(q, lang):
    data = request(lang, {
        "action" : "query",
        "prop" : "langlinks",
        "titles" : q,
        "lllimit" : 500
    })

    data = data["query"]["pages"].values()[0]

    if "langlinks" in data:
        data["total"] = len(data["langlinks"])
    else:
        data["total"] = 0

    return data