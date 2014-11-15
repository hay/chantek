Chantek
=======
An unaspiring HTTP API server written in Python.

## Basic stuff
* [Source on Github](http://github.com/hay/chantek)
* Written by [Hay Kranen](http://github.com/hay)

## Running
To run the server simply run `server.py` root. There's also a `wsgi` configuration example for production use.

For debugging purposes try running `server.py` with the `debug=1` flag:

    $ python server.py --debug=1

## Chantek Commands
Commands go in the `commands` folder. Every command should be in a subfolder, with at least a `__init__.py` file (this should be empty) and a `command.py` file.

The simplest `command.py` file has a structure like this:

    def run(args):
        return "hello world"

`args` gives back all the parameters given in a query. If a query has no named parameter but does accept input (like stdin) this is given as a 'q' parameter.

To write a command with methods (like `command/verb`), write your command like this:

    methods = ("foo")

    def run(args, method):
        if method == "bar":
            return "Bar!"

A command can be known under several aliases, that do nothing more than give the same results under a different name.

    # hello.py

    aliases = ['hola']

    def run(args):
        return "hello world"

    # This command can be reached under both 'hello' and 'hola'

To indicate that a command is cacheable simple write a constant in your command like this:

    CACHEABLE = True

## Who's Chantek?
"Api" pronounced in Dutch means "monkey", and [Chantek](https://en.wikipedia.org/wiki/Chantek) is a very special monkey. He's mastered sign language, and even understands spoken English. Given the fact that API's are all about communication, it made sense to name a HTTP server after a monkey that speaks English.