import inspect
import json
import jsonpickle
import logging
import os
import toml

from argparser import ArgumentsParser
from config import PATH
from util import get_version

COMMANDS_PATH = PATH + "/commands"
VERSION = get_version()

class CommandsManager:
    def __init__(self):
        self.commands = self.parse()

    # This command is used to load the modules when needed
    def get(self, name):
        # For the reason why we need the fromlist argument see
        # < http://stackoverflow.com/questions/2724260 >
        return __import__("commands.%s.command" % name, fromlist="commands")

    # List all commands with arguments and methods
    def listall(self):
        commands = {}
        cmdnames = sorted(list(set(self.commands.values())))

        for cmdname in cmdnames:
            cmd = self.get(cmdname)

            if cmd.__doc__:
                description = cmd.__doc__.strip()
            else:
                description = None

            commands[cmdname] = {
                "aliases" : getattr(cmd, "aliases", None),
                "arguments" : getattr(cmd, "arguments", None),
                "cacheable" : getattr(cmd, "CACHEABLE", None),
                "description" : description,
                "methods" : getattr(cmd, "methods", None),
                "name" : cmdname
            }

        return json.loads(jsonpickle.encode(commands, unpicklable = False))

    def parse(self):
        commands = {}

        logging.info("Parsing commands")

        cmddirs = [c for c in os.listdir(COMMANDS_PATH) if c[0] != "_" and c[0] != "."]

        logging.info("Commands we're going to load %s" % cmddirs)

        for cmdname in cmddirs:
            logging.debug("Parsing <%s>" % cmdname)

            command = self.get(cmdname)
            commands[cmdname] = cmdname

            if hasattr(command, "aliases"):
                for alias in command.aliases:
                    commands[alias] = cmdname

            logging.info("Okay, loaded <%s>" % cmdname)

        logging.debug("Done loading")

        return commands

    def execute(self, params, cmd, cmdmethod, name):
        logging.debug("Executing command %s/%s" % (name, cmdmethod))
        logging.debug("With params " + json.dumps(params, indent = 4))

        if not hasattr(cmd, "run"):
            raise TypeError("Chantek commands required a 'run' method")

        # If there is an 'arguments' dict, use that to fill in default
        # values for the params
        if hasattr(cmd, "arguments"):
            logging.debug(f"Parsing default arguments for <{name}>")
            parser = ArgumentsParser(params, cmd.arguments, cmdmethod)
            params = parser.get_params()

        if hasattr(cmd, "methods"):
            # Python casts tuples with one value to a string, so we
            # need to explicitely make it a tuple
            if isinstance(cmd.methods, str):
                cmd.methods = (cmd.methods, )

            # Check if methods is not something weird
            if not isinstance(cmd.methods, tuple) and \
               not isinstance(cmd.methods, list):
                raise Exception("Methods need to be of type tuple or list")

            if not cmdmethod:
                raise TypeError(f"This command needs one of these methods: {cmd.methods}")
            elif cmdmethod not in cmd.methods:
                raise Exception("Invalid method for <%s>" % name)

            response = cmd.run(params, cmdmethod)
        else:
            # Check if this command wants the 'params' array or not
            spec = inspect.getargspec(cmd.run)

            if len(spec.args) == 0:
                logging.debug("Command has no arguments, not providing params")
                response = cmd.run()
            else:
                response = cmd.run(params)

        return response

    def error(self, msg):
        return { "error" : msg }

    def run(self, cmdname, cmdmethod = None, params = False):
        if cmdname not in self.commands:
            return False, self.error("unknown command %s" % cmdname)

        name = self.commands[cmdname]
        cmd = self.get(name)

        if cmdmethod and not hasattr(cmd, 'methods'):
            return False, self.error("<%s> does not have any methods" % name)

        data_response = {
            "chantek" : VERSION,
            "command" : name,
            "params" : params,
        }

        try:
            response = self.execute(
                params = params,
                cmd = cmd,
                cmdmethod = cmdmethod,
                name = name
            )
        except Exception as e:
            data_response.update({
                "error" : {
                    "message" : "<%s>: %s" % (name, e)
                },
                "response" : False
            })

            if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                raise
        else:
            data_response.update({
                "error" : False,
                "response" : response
            })

        return cmd, data_response