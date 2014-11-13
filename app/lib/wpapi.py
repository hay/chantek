import requests, json, re, time

API_ENDPOINT = "http://%s.wikipedia.org/w/api.php";

def request(lang, params):
    url = API_ENDPOINT % lang
    params.update({ "format" : "json" })
    r = requests.get(url, params = params)

    data = r.json()

    return data

def define(args):
    q = args["q"]
    lang = args["lang"] if "lang" in args else "en"

    data = request(lang, {
        "action" : "query",
        "prop" : "extracts",
        "exintro" : 1,
        "titles" : q
    })

    # Sigh.. awful Wikipedia API crap
    pageid = data['query']['pages'].keys()[0]

    if "-1" in data["query"]["pages"]:
        return False
    else :
        page = data["query"]["pages"][pageid]

        # A bit ugly, but oh well
        page['extract'] = re.sub('<[^<]+?>', '', page['extract']).strip()

        return page

def suggest(args):
    q = args["q"]
    lang = args["lang"] if "lang" in args else "en"

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
def pageviews(args):
    q = args["q"]
    lang = args["lang"] if "lang" in args else "en"

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

def linkshere(args):
    q = args["q"]
    lang = args["lang"] if "lang" in args else "en"

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

def langlinks(args):
    q = args["q"]
    lang = args["lang"] if "lang" in args else "en"

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