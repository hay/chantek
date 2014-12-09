import wikipedia

methods = (
    "article",
    "define",
    "suggest",
    "pageviews",
    "linkshere",
    "langlinks",
    "statistics"
)

def run(args, method):
    if "q" not in args:
        raise Exception("No query given")

    opts = {
        "lang" : args.get("lang", "en"),
        "imgwidth" : args.get("imgwidth", 500),
        "q" : args["q"]
    }

    if method == "article":
        return wikipedia.article(**opts)

    if method == "imgresize":
        return wikipedia.imgresize(**opts)

    if method == "define":
       return wikipedia.define(**opts)

    if method == "suggest":
        return wikipedia.suggest(**opts)

    if method == "pageviews":
        return wikipedia.pageviews(**opts)

    if method == "linkshere":
        return wikipedia.linkshere(**opts)

    if method == "langlinks":
        return wikipedia.langlinks(**opts)

    if method == "statistics":
        langlinks = wikipedia.langlinks(**opts)
        linkshere = wikipedia.linkshere(**opts)
        pageviews = wikipedia.pageviews(**opts)

        return {
            "langlinks" : langlinks["total"],
            "linkshere" : linkshere["total"],
            "pageviews" : pageviews["total"]
        }