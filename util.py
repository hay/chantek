import requests, json, logging
from config import PATH, HTTP_TIMEOUT

def apirequest(url, params):
    logging.debug("Now getting '%s' with parameters %s" % (url, params))

    r = requests.get(url, params = params, timeout = HTTP_TIMEOUT)

    return r.json()

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
def sprintf(string, args):
    return string % args[:string.count("%s")]

def dump(val):
    print json.dumps(val, indent = 4)