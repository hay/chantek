import requests, json, re

API_ENDPOINT = "http://commons.wikimedia.org/w/api.php";
RESIZE_ENDPOINT = "http://commons.wikimedia.org/wiki/Special:Redirect/file/%s"
FILE_PREFIX = "File:"

def parse_imageinfo(data):
    # We don't get the data back in the same order as the files in the API,
    # so we need to do some magic here
    images = {}

    for pageid in data["query"]["pages"]:
        page = data["query"]["pages"][pageid]
        title = page["title"][len(FILE_PREFIX):]

        if "missing" in page:
            images[title] = False
        else:
            images[title] = page["imageinfo"][0]

    return images

def request(params):
    params.update({ "format" : "json" })
    r = requests.get(API_ENDPOINT, params = params)
    data = r.json()
    return data

# Note that this method is a bit of a hack, but it's a lot cheaper
# than getting all the JSON metadata
def imageresize(filename, width = None):
    # We got to remove the Namespace prefix, in all languages :/
    if ":" in filename:
        parts = filename.split(":")
        filename = parts[1]

    filename = RESIZE_ENDPOINT % filename

    if width:
        filename += "?width=" + str(width)

    return filename

def imageinfo(args):
    q = args["q"]
    width = args["width"]
    height = args["height"]

    # FIXME: this doesn't work, because files might have a comma in the filename
    # We need something smarter than this that isn't as ugly as the pipes in the
    # MW api
    """
    # Check if we have one or multiple files
    if "," not in q:
        q = [q]
    else:
        q = q.split(",")
    """
    q = [q]

    # Prefix with 'File:' if it's not there
    q = map(lambda f:f if f.startswith(FILE_PREFIX) else FILE_PREFIX + f, q)

    data = request({
        "action" : "query",
        "titles" : "|".join(q),
        "prop" : "imageinfo",
        "iiurlwidth" : width,
        "iiurlheight" : height,
        "iiprop" : "url|size"
    })

    imageinfo = parse_imageinfo(data)

    return imageinfo