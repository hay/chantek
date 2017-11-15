import argparse, os, json, time, logging, config
from commandsmanager import CommandsManager
from flask import Flask, request, make_response
from urllib.parse import urlparse
from pprint import pprint

app = Flask(__name__)
cache = None
commands = None
IGNORED_URLS = ("/favicon.ico")

def json_response(data):
    if 'pretty' in request.args:
        respdata = json.dumps(data, indent = 4)
    else:
        respdata = json.dumps(data)

    resp = make_response(respdata)

    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Content-Type"] = "application/json; charset=UTF-8"

    return resp

def get_urlpath(url):
    parts = urlparse(url)

    if parts.query is not "":
        return "%s/?%s" % (parts.path, parts.query)
    else:
        return parts.path

def ignore_url(url):
    return url in IGNORED_URLS

def run_command(name, method = None):
    url = get_urlpath(request.url)
    logging.debug("Request: " + url)

    if ignore_url(url):
        return False

    params = request.args.to_dict()

    if config.CACHING.get("enabled", False) and url in cache:
        return cache[url]

    cmd, response = commands.run(
        cmdname = name,
        cmdmethod = method,
        params = params
    )

    cacheable = getattr(cmd, "CACHEABLE", False)
    logging.debug("Command cacheable: " + str(cacheable))

    if not response["error"] and config.CACHING.get("enabled", False) and cacheable:
        # We also need to check if this cache is only for specific methods
        if isinstance(cmd.CACHEABLE, tuple):
            if method in cmd.CACHEABLE:
                cache[url] = response
        else:
            # Not specific, simply cache this
            cache[url] = response

    return response

@app.route('/')
def root():
    return open(config.PATH + "/static/index.html").read()

@app.route('/_commands')
def list_commands():
    logging.debug("Listing all commands")
    return json_response(commands.listall())

@app.route('/<cmdname>/<cmdmethod>')
def command_with_method(cmdname, cmdmethod):
    response = run_command(cmdname, cmdmethod)
    return json_response(response)

@app.route('/<cmdname>')
def command(cmdname):
    response = run_command(cmdname)
    return json_response(response)

def get_cache():
    if not config.CACHING.get("enabled", False):
        return False

    cachemodule = __import__(config.CACHING['type'])

    return cachemodule.Cache(expires = config.CACHING['expires'])

def create_app():
    global cache, commands
    cache = get_cache()
    commands = CommandsManager()
    return app

def main():
    global cache, commands

    logging.info("Starting Chantek server")

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action="store_true")
    parser.add_argument('-nc', '--no-cache', action="store_true")
    parser.add_argument('-t', '--timeout', type=int, default=config.HTTP_TIMEOUT)
    parser.add_argument(
        '-c',
        '--cachingtype',
        choices=('memorycache', 'rediscache'),
        default = config.CACHING["type"]
    )
    args = parser.parse_args()

    config.DEBUG = args.debug

    if args.no_cache:
        config.CACHING["enabled"] = False

    if args.cachingtype:
        config.CACHING["type"] = args.cachingtype

    config.HTTP_TIMEOUT = args.timeout

    app.debug = config.DEBUG

    if config.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    logging.info("Cache configuration: %s" % json.dumps(config.CACHING))
    logging.info("Cache enabled: %s" % config.CACHING.get("enabled", False))

    cache = get_cache()

    commands = CommandsManager()

    logging.info("Going to run a server on %s:%s" %(config.HOST, config.PORT))
    app.run(port = config.PORT, host = config.HOST)

if __name__ == "__main__":
    main()