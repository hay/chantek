from . import wikipedia

CACHEABLE = True

methods = (
    "article",
    "extracts",
    "define",
    "suggest",
    "pageviews",
    "linkshere",
    "langlinks",
    "statistics",
    "links"
)

def run(args, method):
    if "q" not in args:
        raise Exception("No query given")

    lang = args.get("lang", "en")
    q = args["q"]

    opts = {
        "lang" : lang,
        "imgwidth" : args.get("imgwidth", 500),
        "q" : q,
        "cleanup" : args.get("cleanup", None)
    }

    if method == "article":
        return wikipedia.article(**opts)

    if method == "extracts":
        return wikipedia.extracts(**opts)

    if method == "imgresize":
        return wikipedia.imgresize(**opts)

    if method == "define":
       return wikipedia.define(**opts)

    if method == "links":
        return wikipedia.links(q, lang)

    if method == "suggest":
        return wikipedia.suggest(q, lang)

    if method == "pageviews":
        return wikipedia.pageviews(q, lang)

    if method == "linkshere":
        return wikipedia.linkshere(q, lang)

    if method == "langlinks":
        return wikipedia.langlinks(q, lang)

    if method == "statistics":
        langlinks = wikipedia.langlinks(q, lang)
        linkshere = wikipedia.linkshere(q, lang)
        pageviews = wikipedia.pageviews(q, lang)

        return {
            "langlinks" : langlinks["total"],
            "linkshere" : linkshere["total"],
            "pageviews" : pageviews["total"]
        }