import argparse, os, json, glob, time, logging
from cache import Cache
from flask import Flask, request, make_response
from config import PATH
from __init__ import __version__

app = Flask(__name__)
debug = False
caching = True
commands = {}
COMMANDS_PATH = PATH + "/commands"
cache = Cache(filename="cache.json", expires = 3600)
version = __version__
HTTP_TIMEOUT = 5

def create_app():
    parse_commands()
    return app

# This command is used to load the modules when needed
def get_command(name):
    # For the reason why we need the fromlist argument see
    # < http://stackoverflow.com/questions/2724260 >
    return __import__("commands.%s.command" % name, fromlist="commands")

def parse_commands():
    logging.debug("Parsing commands")

    cmddirs = os.walk(COMMANDS_PATH).next()[1]

    for cmdname in cmddirs:
        logging.debug("Parsing <%s>" % cmdname)

        command = get_command(cmdname)
        commands[cmdname] = cmdname

        if hasattr(command, "aliases"):
            for alias in command.aliases:
                commands[alias] = cmdname

        logging.debug("Okay, loaded <%s>" % cmdname)

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

def error(msg):
    return json_response(
        { "error" : msg }
    )

def execute_command(url, params, cmd, cmdmethod, name):
    # Determine if the command is cacheable, and if so, check
    # if its in the cache
    # TODO: This truly needs some refactoring
    logging.debug("Executing command %s/%s" % (name, cmdmethod))

    if hasattr(cmd, "CACHEABLE") and cmd.CACHEABLE == True and caching:
        if url in cache:
            response = cache[url]
        else:
            if hasattr(cmd, "methods"):
                if cmdmethod and cmdmethod in cmd.methods:
                    response = cmd.run(params, cmdmethod)
                else:
                    raise Exception("Invalid method for <%s>" % name)
            else:
                response = cmd.run(params)

            cache[url] = response
    else:
        if hasattr(cmd, "methods"):
            if cmdmethod in cmd.methods:
                response = cmd.run(params, cmdmethod)
            else:
                raise Exception("Invalid method for <%s>" % name)
        else:
            response = cmd.run(params)

    return response

def run_command(cmdname, cmdmethod = None):
    if cmdname not in commands:
        return error("unknown command")

    name = commands[cmdname]
    cmd = get_command(name)

    if cmdmethod and not hasattr(cmd, 'methods'):
        return error("<%s> does not have any methods" % name)

    url = request.url
    params = request.args.to_dict()

    data_response = {
        "chantek" : version,
        "command" : name,
        "params" : params,
    }

    try:
        response = execute_command(
            url = request.url,
            params = request.args.to_dict(),
            cmd = cmd,
            cmdmethod = cmdmethod,
            name = name
        )
    except Exception, e:
        data_response.update({
            "error" : {
                "message" : "<%s>: %s" % (name, e.message)
            },
            "response" : False
        })
    else:
        data_response.update({
            "error" : False,
            "response" : response
        })

    return json_response(data_response)

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