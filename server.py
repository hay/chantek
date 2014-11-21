import argparse, os, json, time, logging
from commands import CommandsManager
from cache import Cache
from flask import Flask, request, make_response
from config import PATH

app = Flask(__name__)
debug = False
caching = True
cache = Cache(filename="cache.json", expires = 3600)
version = __version__
HTTP_TIMEOUT = 5

def json_response(data):
    if 'pretty' in request.args:
        respdata = json.dumps(data, indent = 4)
    else:
        respdata = json.dumps(data)

    if 'callback' in request.args and request.args.get('callback').isalnum():
        callback = request.args.get('callback')
        respdata = '%s(%s)' % (callback, respdata)

    resp = make_response(respdata)

    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Content-Type"] = "application/json; charset=UTF-8"

    return resp

@app.route('/')
def root():
    return open(PATH + "/static/index.html").read()

@app.route('/_commands')
def list_commands():
    logging.debug("Listing all commands")
    return json_response(commands)

@app.route('/<cmdname>/<cmdmethod>')
def command_with_method(cmdname, cmdmethod):
    return run_command(cmdname, cmdmethod)

@app.route('/<cmdname>')
def command(cmdname):
    return run_command(cmdname)

def main():
    global debug, caching
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action="store_true")
    parser.add_argument('-nc', '--no-cache', action="store_true")
    args = parser.parse_args()

    debug = args.debug
    caching = not args.no_cache

    if debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug("Cache enabled:" + str(caching))

    parse_commands()

    app.run(
        debug=args.debug
    )

if __name__ == "__main__":
    main()