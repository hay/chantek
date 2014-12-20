import argparse, os, json, time, logging, config
from commandsmanager import CommandsManager
from cache import Cache
from flask import Flask, request, make_response

app = Flask(__name__)
cache = None
commands = None

def json_response(data):
    if 'pretty' in request.args:
        respdata = json.dumps(data, indent = 4)
    else:
        respdata = json.dumps(data)

    resp = make_response(respdata)

    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Content-Type"] = "application/json; charset=UTF-8"

    return resp

def run_command(name, method = None):
    logging.debug("Request: " + request.url)
    url = request.url
    params = request.args.to_dict()

    if url in cache and config.CACHING:
        return cache[url]

    response = commands.run(
        cmdname = name,
        cmdmethod = method,
        params = params
    )

    if not response["error"] and config.CACHING:
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
    if not config.CACHING:
        return False

    if not hasattr(config, "CACHING_TYPE"):
        raise Exception("Caching enabled, but no caching type set")

    if config.CACHING_TYPE == "memory":
        return Cache(expires = 3600)
    elif config.CACHING_TYPE == "file":
        # There's a bug with the JSON caching leading to files over 5GB!
        raise Exception("File caching is buggy at the moment")
        # return Cache(filename="cache.json", expires = 3600)

def create_app():
    global cache, commands
    commands = CommandsManager()
    cache = get_cache()
    return app

def main():
    global cache, commands

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action="store_true")
    parser.add_argument('-nc', '--no-cache', action="store_true")
    parser.add_argument('-t', '--timeout', type=int, default=config.HTTP_TIMEOUT)
    args = parser.parse_args()

    config.DEBUG = args.debug
    config.CACHING = not args.no_cache
    config.HTTP_TIMEOUT = args.timeout

    app.debug = config.DEBUG

    if config.DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    logging.debug("Cache enabled:" + str(config.CACHING))
    cache = get_cache()

    commands = CommandsManager()

    app.run()

if __name__ == "__main__":
    main()