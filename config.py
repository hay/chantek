import os, logging
PATH = os.path.dirname(os.path.realpath(__file__))
HTTP_TIMEOUT = 5
DEBUG = False
CACHING = {
    "type" : "memorycache", # 'memorycache', 'rediscache'
    "expires" : 3600
}
# logging.basicConfig(filename = 'chantek.log', level = logging.INFO)