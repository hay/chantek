import bengwiki

methods = ("define")

def run(args, method):
    if "q" not in args:
        raise Exception("No query given")

    q = args["q"]

    if method == "define":
        return bengwiki.define(q, expanded = args.get('expanded', False))