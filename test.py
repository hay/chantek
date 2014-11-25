import logging, json
from commandsmanager import CommandsManager

logging.basicConfig(level=logging.DEBUG)
commands = CommandsManager()
print json.dumps(commands.run("wikidata", "entity"), indent = 4)