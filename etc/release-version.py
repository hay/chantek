#!/usr/bin/env python

import sys, os

if len(sys.argv) != 2:
    sys.exit("No valid tag given")

tag = sys.argv[1]

if not tag[0].isdigit():
    sys.exit("First character should be a digit")

PATH = os.path.dirname(os.path.realpath(__file__))
vfile = open( PATH + "/../__init__.py", "w")
vfile.write('__version__ = "%s"' % tag)
os.system("git add " + PATH + "/../__init__.py")
os.system('git commit -m "Tagging release v%s"' % tag)
os.system("git tag v" + tag)
os.system("git push --tags")