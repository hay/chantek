import time, logging

class Cache():
    def __init__(self, expires = 600):
        logging.debug("Enabling memory cache")
        self.expires = expires
        self.cache = {}

    def keys(self):
        return self.cache.keys()

    def __len__(self):
        return len(self.cache)

    def __contains__(self, key):
        return key in self.cache

    def __getitem__(self, key):
        now = int(time.time())

        if key not in self.cache:
            logging.debug("Cache MISS for " + str(key))
            return None

        if (now - self.cache[key]["saved"]) > self.expires:
            # Cache value expired, remove and return None
            logging.debug(str(key) + " expired, empty cache")
            self.cache.pop(key, None)
            return None
        else:
            logging.debug("Cache HIT for " + str(key))
            return self.cache[key]["value"]

    def __setitem__(self, key, value):
        logging.debug("Saving %s in cache" % str(key))

        self.cache[key] = {
            "value" : value,
            "saved" : int(time.time())
        }