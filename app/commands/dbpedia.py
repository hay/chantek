from lib import dbpedia_lookup_api

methods = ("define", "suggest")

def run(args, method):
    if "q" not in args:
        raise Exception("Missing a q parameter")

    params = {
        "q" : args["q"],
        "limit" : args.get("limit", 10)
    }

    if method == "define":
        return dbpedia_lookup_api.define(params)

    if method == "suggest":
        return dbpedia_lookup_api.suggest(params)