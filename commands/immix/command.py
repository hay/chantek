from . import immix

CACHEABLE = True

methods = ("imagesforperson")

def run(args, method):
    if "q" not in args:
        raise Exception("No query given")

    q = args.get("q")

    if method == "imagesforperson":
        return immix.imagesforperson(q)