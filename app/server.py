import argparse, os, json, glob, time
from flask import Flask, request, make_response
from config import PATH

app = Flask(__name__)
debug = False
commands = {}
COMMANDS_PATH = PATH + "/commands"
cache = {}

def create_app():
    parse_commands()
    return app

def get_filename(path):
    name = os.path.splitext(path)[0]
    return os.path.basename(name)

def get_command(name):
    return __import__("commands.%s" % name, fromlist=["commands"])

def parse_commands():
    for f in glob.glob(COMMANDS_PATH + "/*.py"):
        name = get_filename(f)

        if name[0] is not "_":
            cmd = get_command(name)
            commands[name] = name
            if hasattr(cmd, 'aliases'):
                for alias in cmd.aliases:
                    commands[alias] = name

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

def run_command(cmdname, cmdmethod = None):
    if cmdname not in commands:
        return error("unknown command")

    name = commands[cmdname]
    cmd = get_command(name)

    if cmdmethod and not hasattr(cmd, 'methods'):
        return error("<%s> does not have any methods" % name)

    url = request.url
    params = request.args.to_dict()
    now = time.time()

    # Determine if the command is cacheable, and if so, check
    # if its in the cache
    # TODO: This truly needs some refactoring
    if hasattr(cmd, "CACHEABLE") and cmd.CACHEABLE == True:
        if url in cache:
            response = cache[url]
        else:
            if hasattr(cmd, "methods"):
                if cmdmethod and cmdmethod in cmd.methods:
                    response = cmd.run(params, cmdmethod)
                else:
                    return error("Invalid method for <%s>" % name)
            else:
                response = cmd.run(params)

            cache[url] = response
    else:
        if hasattr(cmd, "methods"):
            if cmdmethod in cmd.methods:
                response = cmd.run(params, cmdmethod)
            else:
                return error("Invalid method for <%s>" % name)
        else:
            response = cmd.run(params)

    data_response = {
        "command" : name,
        "params" : params,
        "response" : response
    }

    return json_response(data_response)


@app.route('/')
def root():
    return open(PATH + "/static/index.html").read()

@app.route('/_commands')
def list_commands():
    return json_response(commands)

@app.route('/<cmdname>/<cmdmethod>')
def command_with_method(cmdname, cmdmethod):
    try:
        return run_command(cmdname, cmdmethod)
    except:
        if debug:
            raise

        return error("Something went wrong with this command :/")

@app.route('/<cmdname>')
def command(cmdname):
    try:
        return run_command(cmdname)
    except:
        if debug:
            raise

        return error("Something went wrong with this command :/")

def main():
    global debug
    parser = argparse.ArgumentParser()
    parse_commands()
    parser.add_argument('-d', '--debug', type=bool, default=False)

    args = parser.parse_args()
    debug = args.debug

    app.run(
        debug=args.debug
    )

if __name__ == "__main__":
    main()