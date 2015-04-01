import time, logging, redis, json

KEY_PREFIX = "chantek:"

class Cache():
    def __init__(self, expires = 600):
        logging.debug(u"Enabling redis cache with expire time %s" % expires)
        self.expires = expires
        self.cache = redis.StrictRedis(host='localhost', port=6379, db=0)

    def keys(self):
        return self.cache.keys()

    def __len__(self):
        return self.cache.dbsize()

    def __contains__(self, key):
        return self.cache.exists(KEY_PREFIX + key)

    def __getitem__(self, key):
        if self.cache.exists(KEY_PREFIX + key):
            logging.debug(u"Cache HIT for %s" % key)
            val = self.cache.get(KEY_PREFIX + key)
            return json.loads(val)
        else:
            logging.debug(u"Cache MISS for %s" % key)
            return None

    def __setitem__(self, key, value):
        logging.debug(u"Saving %s in cache" % key)
        value = json.dumps(value)
        self.cache.set(KEY_PREFIX + key, value)

        if self.expires > 0:
            self.cache.expire(KEY_PREFIX + key, self.expires)