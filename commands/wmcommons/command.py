import wmcommons

CACHEABLE = True

methods = ("imageinfo")

def run(args, method):
    if "q" not in args:
        raise Exception("No query given")

    params ={
        "q" : args["q"],
        "width" : args.get("width", 300),
        "height" : args.get("height", 300)
    }

    if method == "imageinfo":
        return wmcommons.imageinfo(params)