import logging, os
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

    def parse(self):
        commands = {}

        logging.debug("Parsing commands")

        cmddirs = os.walk(COMMANDS_PATH).next()[1]

        logging.debug("Commands we're going to load %s" % cmddirs)

        for cmdname in cmddirs:
            logging.debug("Parsing <%s>" % cmdname)

            command = self.get(cmdname)
            commands[cmdname] = cmdname

            if hasattr(command, "aliases"):
                for alias in command.aliases:
                    commands[alias] = cmdname

            logging.debug("Okay, loaded <%s>" % cmdname)

        logging.debug("Done loading")

        return commands

    def execute(self, params, cmd, cmdmethod, name):
        logging.debug("Executing command %s/%s" % (name, cmdmethod))

        if hasattr(cmd, "methods"):
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
            return self.error("unknown command %s" % cmdname)

        name = self.commands[cmdname]
        cmd = self.get(name)

        if cmdmethod and not hasattr(cmd, 'methods'):
            return self.error("<%s> does not have any methods" % name)

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

        return data_response