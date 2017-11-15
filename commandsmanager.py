import logging, os, json
from config import PATH
from __init__ import __version__ as version

COMMANDS_PATH = PATH + "/commands"

class CommandsManager:
    def __init__(self):
        self.commands = self.parse()

    # This command is used to load the modules when needed
    def get(self, name):
        # For the reason why we need the fromlist argument see
        # < http://stackoverflow.com/questions/2724260 >
        return __import__("commands.%s.command" % name, fromlist="commands")

    def listall(self):
        return self.commands

    def parse(self):
        commands = {}

        logging.info("Parsing commands")

        cmddirs = [c for c in os.listdir(COMMANDS_PATH) if c[0] != "_"]

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

        if hasattr(cmd, "methods"):
            # Python casts tuples with one value to a string, so we
            # need to explicitely make it a tuple
            if isinstance(cmd.methods, str):
                cmd.methods = (cmd.methods, )

            # Check if methods is not something weird
            if not isinstance(cmd.methods, tuple):
                raise Exception("Methods need to be of type tuple")

            if cmdmethod in cmd.methods:
                response = cmd.run(params, cmdmethod)
            else:
                raise Exception("Invalid method for <%s>" % name)
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
            "chantek" : version,
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