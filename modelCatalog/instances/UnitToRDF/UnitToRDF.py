import requests
import json
import uuid
import pprint
import datetime
import rdflib
from rdflib import Graph, Literal, BNode, RDF, Namespace, URIRef
from rdflib.namespace import RDFS
import csv
import sys

pp = pprint.PrettyPrinter(indent=2)

# This is a convenience method to handle api responses. The main portion of the notebook starts in the the next cell
def handle_api_response(response, print_response=False):
    parsed_response = response.json()

    if print_response:
        pp.pprint({"API Response": parsed_response})

    if response.status_code == 200:
        return parsed_response
    elif response.status_code == 400:
        raise Exception("Bad request ^")
    elif response.status_code == 403:
        msg = "Please make sure your request headers include X-Api-Key and that you are using correct url"
        raise Exception(msg)
    else:
        now = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
        msg = ("\n\n\n"
               "        ------------------------------------- BEGIN ERROR MESSAGE -----------------------------------------\n"
               "        It seems our server encountered an error which it doesn't know how to handle yet. \n"
               "        This sometimes happens with unexpected input(s). In order to help us diagnose and resolve the issue, \n"
               "        could you please fill out the following information and email the entire message between ----- to\n"
               "        danf@usc.edu:\n"
               "        1) URL of notebook (of using the one from https://hub.mybinder.org/...): [*****PLEASE INSERT ONE HERE*****]\n"
               "        2) Snapshot/picture of the cell that resulted in this error: [*****PLEASE INSERT ONE HERE*****]\n"
               "\n"
               "        Thank you and we apologize for any inconvenience. We'll get back to you as soon as possible!\n"
               "\n"
               "        Sincerely, \n"
               "        Dan Feldman\n"
               "\n"
               "        Automatically generated summary:\n"
               "        - Time of occurrence: {now}\n"
               "        - Request method + url: {response.request.method} - {response.request.url}\n"
               "        - Request headers: {response.request.headers}\n"
               "        - Request body: {response.request.body}\n"
               "        - Response: {parsed_response}\n"
               "\n"
               "        --------------------------------------- END ERROR MESSAGE ------------------------------------------\n"
               "        \n\n\n"
               "        ")

        raise Exception(msg)


def api_request(metric):
    request_headers = {
        'Content-Type': "application/json"
    }
    # For real interactions with the data catalog, use api.mint-data-catalog.org
    url = "http://localhost:5000/get_canonical_json?"

    resp = requests.get(url + "u=" + metric,
                         headers=request_headers)

    # If request is successful, it will return 'result': 'success' along with a list of registered standard variables
    # and their record_ids. Those record_ids are unique identifiers (UUID) and you will need them down the road to
    # register variables
    parsed_response = handle_api_response(resp, print_response=False)
    return parsed_response





def create_metric_url(parsed_response):
    url_string = parsed_response["qudt:abbreviation"]
    url_string1 = url_string + parsed_response["qudt:hasDimension"]
    url_string2 = url_string1.replace("-", "_")
    url_string3 = url_string2.replace(" ","_")
    return url_string3

def print_turtle(store):
    print("--- start: turtle ---")
    print(store.serialize(format="turtle"))
    print("--- end: turtle ---\n")


def get_dim_abbv_typ_from_json(parsed_response):
    abbreviation = parsed_response["qudt:abbreviation"]
    dimension = parsed_response["qudt:hasDimension"]
    type = parsed_response["rdf:type"]
    return dimension, abbreviation, type

# Other way can be to traverse only values of dictionary object
def create_metric_hasPart_url(has_part):
    url = "u_"
    keys_list = ["UNK:prefix_conversion_multiplier", "UNK:prefix_conversion_offset", "UNK:exponent", "UNK:multiplier", "qudt:conversion_multiplier", "qudt:conversion_offset"]
    for i in sorted(has_part):
        # print ((i, has_part[i]))
        if i =="UNK:prefix" or (i =="qudt:quantity" and has_part[i] != "UNKNOWN TYPE"):
            url += has_part[i].split("#")[1].lower()
            url += "_"
        elif i in keys_list:
            if has_part[i] is not None:
                url_string1 = str(int(has_part[i]))
                url_string2 = url_string1.replace("-", "_")
                url_string3 = url_string2.replace(" ", "_")
                url += url_string3
                url += "_"
        elif i == "qudt:symbol" or (i== "qudt:hasDimension" and has_part[i] != "UNKNOWN DIMENSION"
                                    and has_part[i] != "DIMENSION NOT IN MAPPING"):
            url_string2 = has_part[i].replace("-", "_")
            url_string3 = url_string2.replace(" ", "_")
            url += url_string3
            url += "_"

    return url[:-1]


def json_to_rdf(parsed_response, store, MINT, QUDT, UNK):

    metric_url_suffix = create_metric_url(parsed_response)
    metric_dimension, metric_abbreviation, metric_type = get_dim_abbv_typ_from_json(parsed_response)
    # store = Graph()
    # METRIC = "https://w3id.org/mint/instance/"
    # QUDT = "http://qudt.org/1.1/schema/qudt#"
    # UNK = "https://www.w3id.org/mint/unk/"
    # # Bind a few prefix, namespace pairs for pretty output
    # store.bind("metric", METRIC)
    # store.bind("qudt", QUDT)
    # store.bind("UNK", UNK)

    metric = URIRef(MINT+metric_url_suffix)
    qudt = Namespace(QUDT)
    unk = Namespace(UNK)


    store.add((metric, qudt.abbreviation, Literal(metric_abbreviation)))
    store.add((metric, RDFS.label, Literal(metric_abbreviation)))
    if metric_dimension != "":
        store.add((metric, qudt.hasDimension, Literal(metric_dimension)))
    store.add((metric, RDF.type, qudt.Unit))

    has_part = parsed_response["qudt:_hasPart_"]
    for i in range(len(has_part)):
        hasPart_url_1 = create_metric_hasPart_url(has_part[i])
        has_part_url = URIRef(MINT + hasPart_url_1)
        store.add((metric, qudt.hasPart, has_part_url))

        if "UNK:prefix" in has_part[i]:
            store.add((has_part_url, unk.prefix, URIRef(has_part[i]["UNK:prefix"])))

        if "UNK:prefix_conversion_multiplier" in has_part[i]:
            store.add((has_part_url, unk.prefix_conversion_multiplier, Literal(str(has_part[i]["UNK:prefix_conversion_multiplier"]))))

        if "UNK:prefix_conversion_offset" in has_part[i]:
            store.add((has_part_url, unk.prefix_conversion_offset, Literal(str(has_part[i]["UNK:prefix_conversion_offset"]))))

        if "UNK:exponent" in has_part[i]:
            store.add((has_part_url, unk.exponent, Literal(str(has_part[i]["UNK:exponent"]))))

        if "UNK:multiplier" in has_part[i]:
            store.add((has_part_url, unk.multiplier, Literal(str(has_part[i]["UNK:multiplier"]))))

        if "qudt:conversion_multiplier" in has_part[i]:
            store.add((has_part_url, qudt.conversion_multiplier, Literal(str((has_part[i]["qudt:conversion_multiplier"])))))

        if "qudt:conversion_offset" in has_part[i]:
            store.add((has_part_url, qudt.conversion_offset, Literal(str(has_part[i]["qudt:conversion_offset"]))))

        if "qudt:hasDimension" in has_part[i]:
            store.add((has_part_url, qudt.hasDimension, Literal(str(has_part[i]["qudt:hasDimension"]))))

        if "qudt:quantity" in has_part[i]:
            if str(has_part[i]["qudt:quantity"]).startswith("UNKNOWN"):
                store.add((has_part_url, qudt.quantity, Literal(str(has_part[i]["qudt:quantity"]))))
            else:
                store.add((has_part_url, qudt.quantity, URIRef(has_part[i]["qudt:quantity"])))

        if "qudt:symbol" in has_part[i]:
            store.add((has_part_url, qudt.symbol, Literal(str(has_part[i]["qudt:symbol"]))))

    # print_turtle(store)
    # turtle_file = metric_url_suffix +".txt"
    # f = open(turtle_file, "w")
    # f.write(store.serialize(format="turtle"))
    # f.close()
    return metric, store


def preprocess_turtle_file(store):
    MINT = "https://w3id.org/mint/instance/"
    QUDT = "http://qudt.org/1.1/schema/qudt#"
    UNK = "https://www.w3id.org/mint/unk/"
    # Bind a few prefix, namespace pairs for pretty output
    store.bind("mint", MINT)
    store.bind("qudt", QUDT)
    store.bind("UNK", UNK)

    return store, MINT, QUDT, UNK

def create_success_json(success_dict):
    with open('dict.json', 'w') as fp:
        json.dump(success_dict, fp, indent = 2)


def create_error_json(error_dict):
    with open('error.json', 'w') as fp:
        json.dump(error_dict, fp, indent =2)


def create_turtle_file(store):
    f = open('units.ttl', "w")
    f.write(store.serialize(format="turtle"))
    f.close()

if __name__ == '__main__':
    input_file = "Units.json"
    # input_file = sys.argv[1]
    error_dict = dict()
    success_dict = dict()

    store = Graph()
    store, MINT, QUDT, UNK = preprocess_turtle_file(store)

    with open(input_file, "r") as read_file:
        data = json.load(read_file)

        list_dict =  data["results"]["bindings"]
        unit_list = list()
        # print list_dict
        for unit_dict in list_dict:
            unit_list.append(unit_dict["units"]["value"])

        # print unit_list
    # metric = fp.readline()
        count =1
        for metric in unit_list:
            errorflag = 0
            try:
                parsed_response = api_request(metric)
                errorflag = 1
            except:
                error_dict[metric] = "Unit not Defined"

            if errorflag == 1:
                try:
                    URI, store = json_to_rdf(parsed_response, store, MINT, QUDT, UNK)
                    success_dict[metric] = URI
                    # print URI
                    count+=1
                except:
                    error_dict[metric] = "Input Error"

        create_success_json(success_dict)
        create_error_json(error_dict)
        create_turtle_file(store)
    # parsed_response = api_request("C")
    # count =1
    # URI = json_to_rdf(parsed_response, count)
    # count+=1
    # print URI
