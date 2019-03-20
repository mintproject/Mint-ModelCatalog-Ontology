from rdflib import Graph, Literal, BNode, RDF, Namespace, URIRef
from rdflib.namespace import RDFS
import json
from SPARQLWrapper import SPARQLWrapper, JSON
import rdflib
import re


def create_turtle_file(store):
    f = open('variable.ttl', "w")
    f.write(store.serialize(format="turtle"))
    f.close()


def create_error_file(error_dict):
    with open('error.json', 'w') as fp:
        json.dump(error_dict, fp, indent=2)


if __name__ == '__main__':
    store = Graph()
    error_dict = dict()
    property_object_list = list()
    sparql = SPARQLWrapper("http://ontosoft.isi.edu:3030/ds/query")
    sparql.setQuery("""
    PREFIX mc: <https://w3id.org/mint/modelCatalog#>

    SELECT distinct ?u where {
        ?a mc:hasStandardVariable ?u.
    }
    """)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        standard_variable = result["u"]["value"]

        sparql = SPARQLWrapper("http://35.194.43.13:3030/ds/query")
        sparql.setQuery("""
    prefix skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX mc: <https://w3id.org/mint/modelCatalog#>
select ?u ?b ?c
where {
    ?u skos:prefLabel \"""" + standard_variable + """\" @en.
    ?u ?b ?c.
  }
""")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        if not results["results"]["bindings"]:
            error_dict[standard_variable] = "No info available"
        else:
            for result in results["results"]["bindings"]:
                subject = str(result["u"]["value"])
                predicate = str(result["b"]["value"])
                object = str(result["c"]["value"])

                if predicate.endswith("hasProperty"):
                    property_object_list.append(object)
                # print(subject)
                # print predicate
                # print object
                # store.add((URIRef(subject), URIRef(predicate), Literal(object)))
                if not predicate.endswith("subLabel"):
                    if result["u"]["type"] == "uri":
                        if result["b"]["type"] == "uri":
                            if result["c"]["type"] == "uri":
                                store.add((URIRef(result["u"]["value"]), URIRef(result["b"]["value"]),
                                           URIRef(result["c"]["value"])))
                            else:
                                store.add((URIRef(result["u"]["value"]), URIRef(result["b"]["value"]),
                                           Literal(result["c"]["value"])))

    for property_object in property_object_list:
        sparql_query = """
        select  ?b ?c
                where
                {

                <""" +property_object+ """> ?b ?c.
                }
        """
        sparql.setQuery(sparql_query)
        sparql.setReturnFormat(JSON)
        property_results = sparql.query().convert()

        for property_result in property_results["results"]["bindings"]:
            subject = property_object
            predicate = property_result["b"]["value"]
            obj = str(property_result["c"]["value"])

            if not predicate.endswith("subLabel"):
                if predicate.endswith("hasUnits"):
                    obj1 = obj.replace("^", "")
                    obj = obj1

                if property_result["b"]["type"] == "uri":
                    if property_result["c"]["type"] == "uri":
                        store.add((URIRef(subject), URIRef(predicate),
                                   URIRef(obj)))
                    else:
                        store.add((URIRef(subject), URIRef(predicate),
                                   Literal(obj)))

    create_turtle_file(store)
    create_error_file(error_dict)
