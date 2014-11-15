import requests, json
from config import PATH

def apirequest(url, params, debug = False):
    if debug:
        print "Now getting '%s' with parameters %s" % (url, params)

    r = requests.get(url, params = params)
    data = r.json()
    return data

def mapobj(obj, fn):
    newobj = {}

    for (key, val) in obj.iteritems():
        newobj[key] = fn(val)

    return newobj

def load_json(filename):
    json_data = open(filename, "r").read()
    return json.loads(json_data)

def load_datafile(filename):
    path = PATH + "/commands/" + filename + ".json"
    return load_json(path)

# This variable replacement stuff is pretty ugly here, because of the
# variable number of arguments, but i don't really know how to do this
# otherwise
def sprintf (string, args):
    return string % args[:string.count("%s")]

