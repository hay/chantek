from command import Command
from lib import wmcommons

def run(args):
    cmd = Command(args = args)

    cmd.add_param("method", options = ["imageinfo"])
    cmd.add_param("q")
    cmd.add_param("width")
    cmd.add_param("height")

    if cmd.has_error():
        return cmd.get_error()

    if args["method"] == "imageinfo":
        return wmcommons.imageinfo(cmd.get_params())