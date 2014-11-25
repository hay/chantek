import argparse, os, json, time, logging, config
from commandsmanager import CommandsManager
from cache import Cache
from flask import Flask, request, make_response

app = Flask(__name__)
cache = Cache(filename="cache.json", expires = 3600)

def json_response(data):
    if 'pretty' in request.args:
        respdata = json.dumps(data, indent = 4)
    else:
        respdata = json.dumps(data)

    resp = make_response(respdata)

    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Content-Type"] = "application/json; charset=UTF-8"

    return resp

@app.route('/')
def root():
    return open(config.PATH + "/static/index.html").read()

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
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action="store_true")
    parser.add_argument('-nc', '--no-cache', action="store_true")
    args = parser.parse_args()

    config.DEBUG = args.debug
    config.CACHING = not args.no_cache

    app.debug = config.DEBUG

    if config.DEBUG:
        logging.basicConfig(level=logging.DEBUG)


    logging.debug("Cache enabled:" + str(config.DEBUG))

    app.run()

if __name__ == "__main__":
    main()