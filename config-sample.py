import os, logging
PATH = os.path.dirname(os.path.realpath(__file__))
HTTP_TIMEOUT = 5
DEBUG = False
CACHING = {
    "type" : "rediscache", # 'memorycache', 'rediscache'
    "expires" : 3600
}
REDIS = {
    "host" : "localhost",
    "port" : 6379,
    "db" : 0
}
PORT = 5000
# logging.basicConfig(filename = 'chantek.log', level = logging.INFO)