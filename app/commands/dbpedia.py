from command import Command
from lib import dbpedia_lookup_api

def run(args):
    cmd = Command(args = args)

    cmd.add_param("method", options = ("define", "suggest"))
    cmd.add_param("q")
    cmd.add_param("limit", default = 10)

    if cmd.has_error():
        return cmd.get_error()

    if args["method"] == "define":
        return dbpedia_lookup_api.define(cmd.get_params())
    elif args["method"] == "suggest":
        return dbpedia_lookup_api.suggest(cmd.get_params())