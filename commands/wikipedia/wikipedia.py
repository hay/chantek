import requests, json, re, time
from pyquery import PyQuery as pq
from commands.wmcommons import wmcommons
from jq import jq
from dataknead import Knead

API_ENDPOINT = "https://%s.wikipedia.org/w/api.php"
WIKIDATA_ENDPOINT = "https://www.wikidata.org/w/api.php"

def request(lang, params, wikidata = False):
    if wikidata:
        url = WIKIDATA_ENDPOINT
    else:
        url = API_ENDPOINT % lang

    params.update({ "format" : "json" })
    r = requests.get(url, params = params)
    data = r.json()
    return data

def _getfirstpage(data):
    if "-1" in data["query"]["pages"]:
        return False

    # Sigh.. awful Wikipedia API crap
    pageid = list(data['query']['pages'].keys())[0]
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

def _article(q, lang):
    opts = {
        "action" : "query",
        "prop" : "revisions",
        "titles" : q,
        "rvprop" : "content",
        "rvparse" : 1
    }

    data = request(lang, opts)
    text = _getfirstpage(data)["revisions"][0]["*"]

    return text

def _getimages(q, lang, imgwidth):
    images = articleimages(q, lang)

    if images:
        images = imageinfo(images, lang)
        # Remove all 'local' images, we can't redirect those to Commons
        images = [ i for i in images if isinstance(i, dict) and i.get("imagerepository", None) ]

        for img in images:
            img["thumb"] = wmcommons.imageresize(img["title"], imgwidth)
    else:
        return None

    return images

selectors_to_remove = (
    ".infobox",
    ".reference",
    ".toc",
    ".mw-editsection",
    ".thumb",
    ".image",
    ".toccolours",
    ".noprint",
    ".credits",
    ".navigatiesjabloon"
)

def _cleanup(html):
    d = pq(html)

    [d.remove(s) for s in selectors_to_remove]
    d.find(".references").parent().remove()
    d.find("#Externe_links").parent().next().remove()
    d.find("#Externe_link").parent().next().remove()
    d.find("#Referenties").remove()
    d.find("#Externe_links").remove()
    d.find("#Externe_link").remove()

    for a in d.find("a[href]"):
        pq(a).removeAttr('href')

    # Stupid inline styles
    for el in d.find("[style]"):
        pq(el).removeAttr('style')

    text = d.html().strip()
    return text if text else False

def article(q, lang, imgwidth, cleanup):
    text = _article(q, lang)

    if cleanup:
        text = _cleanup(text)

    return {
        "text" : text,
        "thumbnail" : thumbnail(q, lang, imgwidth),
        "images" : _getimages(q, lang, imgwidth)
    }

def extracts(q, lang, imgwidth, cleanup):
    text = _extracts(q, lang, False)

    if not text or text["extract"].strip() == "":
        return False

    text = text["extract"]

    return {
        "text" : text,
        "thumbnail" : thumbnail(q, lang, imgwidth),
        "images" : _getimages(q, lang, imgwidth)
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

    if not data or "thumbnail" not in data:
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

    return list(map(_imageinfo_format, list(data["query"]["pages"].values())))

def articleimages(q, lang):
    data = request(lang, {
        "action" : "query",
        "prop" : "images",
        "titles" : q
    })

    page = _getfirstpage(data)

    if not page or not "images" in page:
        return False

    return [x["title"] for x in page["images"]]

def define(q, lang, imgwidth, cleanup):
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
    for (key, view) in stats["daily_views"].items():
        total = total + int(view)

    stats["total"] = total

    return stats

def _formatlink(link):
    if "pageprops" in link:
        link["wikidata"] = link["pageprops"].get("wikibase_item", None)
        link["image"] = link["pageprops"].get("page_image", None)
        link.pop("pageprops", None)

    return link

# Returns all internal links in a page, with a Wikidata ID and page image
def links(q, lang):
    data = request(lang, {
        "action" : "query",
        "prop" : "pageprops",
        "redirects" : 1,
        "titles" : q,
        "generator" : "links",
        "titles" : q,
        "gplnamespace" : 0,
        "gpllimit" : 500
    })

    if not data:
        return False

    return list(map(_formatlink, list(data["query"]["pages"].values())))

def linkshere(q, lang):
    data = request(lang, {
        "action" : "query",
        "prop" : "linkshere",
        "titles" : q,
        "lhlimit" : 500
    })

    data = list(data["query"]["pages"].values())[0]

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

    data = list(data["query"]["pages"].values())[0]

    if "langlinks" in data:
        data["total"] = len(data["langlinks"])
    else:
        data["total"] = 0

    return data

def _add_descriptions_to_qids(pages, lang):
    qids = [p["qid"] for p in pages]

    data = request(lang = None, wikidata = True, params = {
        "action" : "wbgetentities",
        "ids" : "|".join(qids),
        "props" : "descriptions",
        "languages" : lang
    })

    descriptions = data["entities"]

    for p in pages:
        qid = p["qid"]
        desc = descriptions[qid]["descriptions"].get("nl", None)

        if desc:
            p["description"] = desc.get("value", None)
        else:
            p["descrtipion"] = None

    return pages

def _add_qids_to_pageids(pages, lang):
    pageids = [str(p["pageid"]) for p in pages]

    data = request(lang, {
        "action" : "query",
        "prop" : "pageprops",
        "pageids" : "|".join(pageids)
    })

    if not "query" in data:
        for p in pages:
            p["qid"] = None

        return pages

    result = data["query"]["pages"]

    for page in pages:
        pid = page["pageid"]
        page["qid"] = result[str(pid)]["pageprops"]["wikibase_item"]

    pages = _add_descriptions_to_qids(pages, lang)

    return pages

def reconcile(q, lang):
    data = request(lang, {
        "action" : "query",
        "list" : "search",
        "srsearch" : q,
        "srlimit" : 3,
        "srinterwiki" : True,
        "srprop" : "score|pageid",
        "utf8" : True
    })

    results = jq(".query.search").transform(data)
    results = _add_qids_to_pageids(results, lang)

    return results