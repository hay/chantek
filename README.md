Chantek
=======
An unaspiring read-only HTTP API server written in Python 3.

Easily extended with your own commands.

Includes default commands for querying Wikipedia, Wikidata and the Magic 8-Ball.

Try the live demo: [http://api.haykranen.nl](http://api.haykranen.nl)

## Reference
* [Source on Github](http://github.com/hay/chantek)
* Written by [Hay Kranen](http://github.com/hay)

## Running (production)
To run the server simply run `server.py` in the root. There's also a `uwsgi.ini` configuration example for [production use](http://www.haykranen.nl/2014/11/15/running-a-python-flask-app-with-nginx-using-uwsgi/).

Another option is simply running this with an init / systemd script (see `etc/ubuntu-init.conf` for an example), and proxy the calls using something like Nginx. See `etc/nginx-example.conf` for an example.

## Running (development)

For debugging purposes try running `server.py` with the `debug=1` flag:

    $ python server.py --debug=1

Or simply use `-d`

    $ python server.py -d

To disable caching use the `-nc` flag.

This will run your Chantek server on port 5000.

For a list of all commands try going to `http://localhost:5000/_commands`.

All commands can be queried like this:

    $ curl http://localhost:5000/<command>?param1=foo&param2=bar

Commands with methods (see below) can be called like this:

    $ curl http://localhost:5000/<command>/<method>?param1=foo&param2=bar

Commands return their data as JSON following a consistent format:

    $ curl http://localhost:5000/wikipedia/define?q=Chantek

    {
        // Contains the original parameters
        "params": {
            "q": "Chantek"
        },

        // Did an error occur during your call?
        "error": false,

        // Contains the original command
        "command": "wikipedia",

        // Response from the command
        "response": {
            "extract": "Chantek (born December 17, 1977, at the Yerkes Regional Primate Research Center in Atlanta, Georgia) is a male orangutan who has mastered the use of a number of intellectual skills, including sign language, taught by American anthropologists Lyn Miles and Ann Southcombe. In Malay and Indonesian, cantik (pronounced chanteek) means \"lovely\" or \"beautiful\".",
            "ns": 0,
            "pageid": 1577406,
            "title": "Chantek"
        },

        // Version number
        "chantek": "0.1.0"
    }

HTTP responses by default are [CORS](http://enable-cors.org/) enabled for use in web applications.

## Chantek Commands
Commands go in the `commands` folder. Every command should be in a subfolder, with at least a `__init__.py` file (this should be empty) and a `command.py` file.

For example:

    chantek/
        commands/
            mycommand/
                __init__.py
                command.py
                otherlib.py
                data.json

The simplest `command.py` file has a structure like this:

    def run(args):
        return "hello world"

`args` gives back all the url arguments given in the query as a dict.

To write a command with methods (like `command/verb`), write your command like this:

    methods = ("foo")

    def run(args, method):
        if method == "bar":
            return "Bar!"

A command can be known under several aliases:

    # hello.py

    aliases = ['hola']

    def run(args):
        return "hello world"

    # This command can be reached under both 'hello' and 'hola'

To indicate that a command is cacheable simple write a constant in your command like this:

    CACHEABLE = True

This will save every unique URL query to an configured cache.

You can make only some methods cacheable, to do so, simply use a tuple instead of a bool

    methods = ("search", "random")
    CACHEABLE = ("search") # 'random' should not be cacheable

## Caching
Currently there are two caching options: in-memory (this simply saves stuff to a dict), or [Redis](http://redis.io). Optionally, an expire timeout can be given in seconds. See the `config.py` file for instructions on how to configure your cache.

# Packages you need
I should probably make a `requirements.txt` file sometime, for now run this:

    sudo pip install flask requests pyquery lxml redis xmltodict python-dateutil

## TODO
Things that are not working yet and should be done:
* Commands should be self-documenting, and display help in the API
* Going to the root of the server (e.g. `http://localhost:5000`) should return an interactive console
* More commands!

## Who's Chantek?
"Api" pronounced in Dutch means "monkey", and [Chantek](https://en.wikipedia.org/wiki/Chantek) is a very special monkey indeed. He's mastered sign language, and even understands spoken English. Given the fact that API's are all about communication, it made sense to name a HTTP server after a monkey that speaks English.