from rdflib import Graph
from dataknead import Knead
from collections import namedtuple
import requests
import json

RDF_ENDPOINT = "https://www.wikidata.org/wiki/Special:EntityData/%s.rdf"

Namespace = namedtuple("Namespace", "uri name")
NS_DESCRIPTION = Namespace("http://schema.org/description", "description")
NS_NAME = Namespace("http://schema.org/name", "name")
NS_ENTITY = Namespace("http://www.wikidata.org/entity/", "entity")
NS_ENTITY_STATEMENT = Namespace("http://www.wikidata.org/entity/statement/", "entity_statement")
NS_PROP_STATEMENT = Namespace("http://www.wikidata.org/prop/statement/", "prop_statement")


class WikidataEntityLD:
    def __init__(self, qid, languages = ""):
        self.qid = qid
        self.languages = languages.split(",")
        self.rdf = self.get_rdf()

    def _entityvalues(self, item, idns):
        tree = {
            "uri" : item["@id"]
        }

        for ns in (NS_NAME, NS_DESCRIPTION):
            if ns.uri in item:
                tree[ns.name] = { i["@language"]:i["@value"] for i in item[ns.uri] }

                # Do we only want a selection of languages?
                if self.languages:
                    tree[ns.name] = { k:v for k,v in tree[ns.name].items() if k in self.languages}

        return tree

    def _get_by_namespace(self, tree, namespace):
        items = Knead(tree).filter(lambda i:i["@id"].startswith(namespace.uri))
        return items.data()

    def _statementvalues(self, statement, uri):
        prop = [
            { "property_uri": key, "values" : val }
            for key, val in statement.items() if key.startswith(uri)
        ]

        if len(prop) == 1:
            return prop[0]
        else:
            return None

    def get_rdf(self):
        r = requests.get(RDF_ENDPOINT % self.qid)
        return r.text

    def as_json_ld(self):
        graph = Graph().parse(data=self.rdf, format='xml')
        jsonld = graph.serialize(format='json-ld', indent=4)
        return json.loads(jsonld)

    def as_json_ld_simplified(self):
        tree = self.as_json_ld()

        entities = self._get_by_namespace(tree, NS_ENTITY)
        entities = { i["@id"]:self._entityvalues(i, NS_ENTITY.uri) for i in entities }

        statements = self._get_by_namespace(tree, NS_ENTITY_STATEMENT)
        statements = [self._statementvalues(s, NS_PROP_STATEMENT.uri) for s in statements]

        for statement in statements:
            if statement:
                uri = statement["property_uri"].replace("prop/statement", "entity")
                statement["property"] = entities.get(uri, None)

                for value in statement["values"]:
                    if "@id" in value:
                        value["entity"] = entities.get(value["@id"], None)

                    if "@value" in value:
                        value["value"] = value["@value"]


        return {
            "entities" : entities,
            "statements" : statements
        }