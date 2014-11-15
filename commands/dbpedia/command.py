import lookup

methods = ("define", "suggest")

def run(args, method):
    if "q" not in args:
        raise Exception("Missing a q parameter")

    params = {
        "q" : args["q"],
        "limit" : args.get("limit", 10)
    }

    if method == "define":
        return lookup.define(params)

    if method == "suggest":
        return lookup.suggest(params)