import time, logging, redis, json, config, json

KEY_PREFIX = "chantek:cache:"

class Cache():
    def __init__(self, expires = 600):
        logging.debug("Enabling redis cache with expire time %s" % expires)
        self.expires = expires
        conf = config.REDIS
        logging.debug("Redis cache has these parameters: " + json.dumps(conf))
        self.cache = redis.StrictRedis(
            host = conf["host"],
            port = conf["port"],
            db = conf["db"]
        )

        # Try getting the size, if this fails Redis is properly not online
        try:
            self.cache.dbsize()
        except:
            logging.error("Could not connect to Redis database!")

    def keys(self):
        return list(self.cache.keys())

    def __len__(self):
        return self.cache.dbsize()

    def __contains__(self, key):
        return self.cache.exists(KEY_PREFIX + key)

    def __getitem__(self, key):
        if self.cache.exists(KEY_PREFIX + key):
            logging.debug("Cache HIT for %s" % key)
            val = self.cache.get(KEY_PREFIX + key)
            return json.loads(val)
        else:
            logging.debug("Cache MISS for %s" % key)
            return None

    def __setitem__(self, key, value):
        logging.debug("Saving %s in cache" % key)
        value = json.dumps(value)
        self.cache.set(KEY_PREFIX + key, value)

        if self.expires > 0:
            self.cache.expire(KEY_PREFIX + key, self.expires)