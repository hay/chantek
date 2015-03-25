import immix

methods = ("byperson")

def run(args, method):
    if "gtaa" not in args:
        raise Exception("No query given")

    if method == "byperson":
        return immix.byperson(args['gtaa'])