import util, json, time, math

from commands.wmcommons import wmcommons

API_ENDPOINT = "http://www.wikidata.org/w/api.php";

class WikidataEntity:
    def __init__(self):
        self.entitycache = {}

        # If set to 'True' and only one language is given, the value
        # is directly given as value for a key instead of an object
        # e.g. { "propery_labels" : "Birth name" } vs { "property_labels" : { "en" : "Birth name" }}
        self.flattenlanguages = True

    def get_claim_values(self, claim):
        snak = claim["mainsnak"]

        if "datatype" not in snak:
            return claim

        datatype = snak["datatype"]
        val = { "datatype" : datatype }
        value = snak["datavalue"]["value"]

        if datatype == "wikibase-item":
            qid = "Q" + str(value["numeric-id"])
            val["value"] = qid
            self.entitycache[qid] = False
        elif datatype == "monolingualtext":
            # Probably a bit hacky really
            val["value"] = value["text"]
        else:
            val["value"] = value

        return val

    def get_claims(self, clist):
        """
        This is a two-set process, because we don't know the labels of the
        properties and claims, we use the id's only the first time, then
        get the labels for all of these ids using a second query
        """

        claims = []

        for (prop, claimlist) in clist.iteritems():
            values = map(self.get_claim_values, claimlist)
            self.entitycache[prop] = False # cache for query later

            claims.append({
                "property_id" : prop,
                "values" : values
            })

        # For the entitycache we don't get any entites, otherwise we'll end
        # in an endless loop
        if not self.get_entity:
            return claims

        # Okay, now get the labels for all queued entities
        we = WikidataEntity()

        self.entitycache = we.get_entity({
            "ids" : self.entitycache,
            "languages" : self.languages,
            "props" : ("labels", "descriptions"),
            "get_references" : False # That's pretty important, otherwise we'll get an endless loop
        })

        # Loop over the newly gotten entities and re-fill those values in claims
        for claim in claims:
            if claim["property_id"] not in self.entitycache:
                continue

            propinfo = self.entitycache[claim["property_id"]]

            if "descriptions" in propinfo:
                claim["property_descriptions"] = propinfo["descriptions"]

            if "labels" in propinfo:
                claim["property_labels"] = propinfo["labels"]

            for val in claim["values"]:
                if "datatype" not in val:
                    continue

                if val["datatype"] != "wikibase-item":
                    continue

                if val["value"] not in self.entitycache:
                    continue

                valinfo = self.entitycache[val["value"]]

                if "descriptions" in valinfo:
                    val["value_descriptions"] = valinfo["descriptions"]

                if "labels" in valinfo:
                    val["value_labels"] = valinfo["labels"]

        # Sort by property ID, usually the lower numbers are more imporant
        claims.sort(key = lambda c:int(c['property_id'][1:]))

        return claims

    def get_aliases(self, aliases):
        for (key, val) in aliases.iteritems():
            aliases[key] = map(lambda i:i["value"], val)

        return aliases

    def get_sitelinks(self, sitelinks):
        links = {}

        for (key, val) in sitelinks.iteritems():
            lang = val["site"].replace("wiki", "")
            title = val["title"]

            if lang not in self.languages:
                continue

            if lang == "commons":
                url = "http://commons.wikimedia.org/wiki/" + title
            else:
                url = "http://%s.wikipedia.org/wiki/%s" % (lang, title)

            links[lang] = {
                "title" : title,
                "url" : url
            }

        return links

    def flatten(self, item):
        lang = self.languages[0]

        for key in ("descriptions", "labels", "aliases"):
            if key in item:
                item[key] = item[key][lang]

        if "claims" not in item:
            return item

        for index, claim in enumerate(item["claims"]):
            for key in ("property_labels", "property_descriptions"):
                if key in item["claims"][index]:
                    if type(item["claims"][index][key]) is list:
                        item["claims"][index][key] = item["claims"][index][key][lang]

            for value in claim["values"]:
                for key in ("value_descriptions", "value_labels"):
                    if key in item["claims"][index]["values"]:
                        if type(item["claims"][index]["values"][key]) is list:
                            item["claims"][index]["values"][key] = item["claims"][index]["values"][key][lang]

        return item

    def format(self, d):
        item = {
            "id" : d["id"]
        }

        if "aliases" in self.props and "aliases" in d:
            item["aliases"] = self.get_aliases(d["aliases"])

        if "claims" in self.props and "claims" in d:
            item["claims"] = self.get_claims(d["claims"])

        if "descriptions" in self.props and "descriptions" in d:
            item["descriptions"] = util.mapobj(d["descriptions"], lambda i:i["value"])

        if "labels" in self.props and "labels" in d:
            item["labels"] = util.mapobj(d["labels"], lambda i:i["value"])

        if "sitelinks" in self.props and "sitelinks" in d:
            item["sitelinks"] = self.get_sitelinks(d["sitelinks"])

        if len(self.languages) == 1 and self.flattenlanguages:
            item = self.flatten(item)

        return item

    def iterimages(self, entities):
        for qid, entity in entities.iteritems():
            for claim in entity["claims"]:
                values = claim["values"][0]

                if values["datatype"] == "commonsMedia":
                    yield values, entity

    def resolve_images(self, entities, imagewidth, imageheight):
        # First extract all the images, from the claims, get all of them
        # in one go, and replace the claims
        imagePaths = []

        for imagevalues, entity in self.iterimages(entities):
            imagePaths.append( imagevalues["value"] )

        # So, we do we actually *have* images for this entity?
        if len(imagePaths) == 0:
            return entities

        # Now get all the images
        imageinfo = wmcommons.imageinfo({
            "q" : ",".join(imagePaths),
            "width" : imagewidth,
            "height" : imageheight
        })

        # Okay, now re-integrate these images into the entity
        for imagevalues, entity in self.iterimages(entities):
            imagePath = imagevalues["value"]

            if imagePath in imageinfo:
                imagevalues["image"] = imageinfo[imagePath]
                entity["image"] = imageinfo[imagePath]

        return entities

    def entity_request(self, ids):
        r = util.apirequest(API_ENDPOINT, {
            "languages" : "|".join(self.languages),
            "action" : "wbgetentities",
            "ids" : "|".join(ids),
            "props" : "|".join(self.props),
            "format" : "json"
        })

        if "success" in r:
            return r["entities"]
        else:
            raise Exception("Invalid or bad API request")

    def get_entity(self, params):
        self.languages = params["languages"]
        self.ids = params["ids"]
        self.get_references = params["get_references"]
        self.props = params["props"]
        self.flattenlanguages = params.get("flattenlanguages") or True

        # For benchmarking purposes
        now = time.time()

        # We need this ugly hack for requests with more than 50 ids
        entities = {}

        if isinstance(self.ids, dict):
            ids = self.ids.keys()
        else:
            ids = self.ids

        reqcount = int(math.ceil(len(ids) / 50.0))

        for reqiterator in range(reqcount):
            idstart = reqiterator * 50
            idend = (reqiterator + 1) * 50
            ids_to_get = ids[idstart:idend]
            req = self.entity_request(ids_to_get)
            entities.update(req)


        for id_, entity in entities.items():
            entities[id_] = self.format(entities[id_])

        return entities

    def entity(self, args):
        # Parse the query
        q = args["q"]

        # Check if we have one or multiple entity ID
        if "," in q:
            q = q.split(",")
        else:
            q = [q]

        # Now add a "Q" in front of the id if its not already there
        q = map(lambda qid:qid if qid[0] == "Q" else "Q" + qid, q)

        entity = self.get_entity({
            "ids" : q,
            "languages" : args["language"].split(","), # note that 'language' is not plural here
            "props" : ("info", "labels", "descriptions", "datatype", "claims", "aliases", "sitelinks"),
            "get_references" : True,
            "flattenlanguages" : args.get("flattenlanguages") or True
        })

        if args.get("resolveimages", False):
            entity = self.resolve_images(
                entity,
                args["imagewidth"],
                args["imageheight"]
            )

        return entity

    def random(self, args):
        r = util.apirequest(API_ENDPOINT, {
            "languages" : "|".join(args["language"]),
            "action" : "query",
            "list" : "random",
            "rnnamespace" : 0,
            "format" : "json"
        })

        print r

        if "query" in r:
            return r["query"]["random"][0]["title"]
        else:
            return {"error" : "Could not get a random item"}