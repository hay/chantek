from _context import commandsmanager
from commandsmanager import CommandsManager
import logging

def main():
    commands = CommandsManager()

    for command in commands.listall():
        print("Testing %s..." % command, end = "")

        cmd, result = commands.run(
            cmdname = command,
            params = {}
        )

        if not result["error"]:
            print("okay!")
        else:
            print("Errror: %s" % result["error"])

if __name__ == "__main__":
    main()