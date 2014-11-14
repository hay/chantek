from lib import wpapi

methods = ("define", "suggest", "pageviews", "linkshere", "langlinks", "statistics")

def run(args, method):
    if "q" not in args:
        raise Exception("No query given")

    opts = {
        "lang" : args.get("lang", "en"),
        "q" : args["q"]
    }

    if method == "define":
       return wpapi.define(opts)

    if method == "suggest":
        return wpapi.suggest(opts)

    if method == "pageviews":
        return wpapi.pageviews(opts)

    if method == "linkshere":
        return wpapi.linkshere(opts)

    if method == "langlinks":
        return wpapi.langlinks(opts)

    if method == "statistics":
        langlinks = wpapi.langlinks(opts)
        linkshere = wpapi.linkshere(opts)
        pageviews = wpapi.pageviews(opts)

        return {
            "langlinks" : langlinks["total"],
            "linkshere" : linkshere["total"],
            "pageviews" : pageviews["total"]
        }