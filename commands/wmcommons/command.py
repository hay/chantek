from . import wmcommons

CACHEABLE = True
arguments = {
    "q" : {
        "required" : True,
        "type" : str
    },
    "height" : 300,
    "width" : 300
}
methods = ("imageinfo")

def run(args, method):
    if method == "imageinfo":
        return wmcommons.imageinfo(args)