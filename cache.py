import time, logging, json, os

class Cache():
    def __init__(self, filename = False, expires = 600):
        self.expires = expires
        self.filename = False
        self.file = False
        self.cache = {}

        if not filename:
            # No need for writing to disk, simply use in-memory stuff
            logging.debug("No filename, no syncing needed")
        else:
            logging.debug("Saving cache to disk")

            self.filename = filename

            # First check if there is an existing file we need to read
            # for the cache
            if os.path.isfile(self.filename):
                f = open(self.filename, "r")

                try:
                    data = json.loads(f.read())
                except ValueError:
                    logging.debug("JSON was invalid")
                else:
                    self.cache = data

                f.close()

            # Open for saving
            self.file = open(self.filename, "w")

    def keys(self):
        return self.cache.keys()

    def sync(self):
        if not self.filename:
            return

        data = json.dumps(self.cache)
        self.file.write(data)

    def __del__(self):
        if file in self:
            logging.debug("Closing cache")
            self.file.close()

    def __len__(self):
        return len(self.cache)

    def __contains__(self, key):
        return key in self.cache

    def __getitem__(self, key):
        now = int(time.time())

        if key not in self.cache:
            logging.debug(str(key) + " not in cache")
            return None

        if (now - self.cache[key]["saved"]) > self.expires:
            # Cache value expired, remove and return None
            logging.debug(str(key) + " expired, empty cache")
            self.cache.pop(key, None)
            return None
        else:
            logging.debug("Cache hit for " + str(key))
            return self.cache[key]["value"]

    def __setitem__(self, key, value):
        logging.debug("Saving %s in cache" % str(key))

        self.cache[key] = {
            "value" : value,
            "saved" : int(time.time())
        }

        self.sync()