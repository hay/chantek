"""
This is a command line script for the Chantek server

Usage:
python cli.py <cmdname> -m <method> -q <query> -ak <argument key> -av <argument value>
"""

import json, argparse, logging, sys, shutil
from .commandsmanager import CommandsManager

commands = CommandsManager()
parser = argparse.ArgumentParser(description = "A command line script for the Chantek server.")

def run(args):
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.list:
        return "\n".join(list(commands.listall().keys()))

    if not args.cmdname:
        parser.print_help()
        return

    result = commands.run(
        cmdname = args.cmdname,
        cmdmethod = args.method,
        params = {
            "q" : args.query
        }
    )

    if result["error"]:
        return result["error"]

    if not args.verbose:
        result = result["response"]

    return result

def init_command(name):
    print("Creating new command '%s'" % name)
    shutil.copytree("etc/command-template", "commands/%s" % name)

def main():
    parser.add_argument('cmdname', nargs = '?', help="Name of the command")
    parser.add_argument('-m', '--method', help="Command method")
    parser.add_argument('-q', '--query', help="Default query")
    parser.add_argument('-l', '--list', help="List all available commands", action="store_true")
    parser.add_argument('-d', '--debug', help="Show debug data", action="store_true")
    parser.add_argument('-v', '--verbose', help="Show verbose results", action="store_true")
    parser.add_argument('--init', help="Create new command")

    args = parser.parse_args()

    if args.init:
        init_command(args.init)
        sys.exit()

    result = run(args)

    if isinstance(result, str):
        print(result)
    else:
        print(json.dumps(result, indent = 4))

if __name__ == "__main__":
    main()