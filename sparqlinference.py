#!/usr/bin/env python3

import sys
import io
import csv
import json
import getopt
import urllib.request
import prettytable
import RDF

def main(argv):
    endpoint = None
    modelFile = None
    query = None

    try:
        opts, args = getopt.getopt(argv, "i:o:r:", ["input", "output", "rules"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-i", "--input"):
            inputPath = a
        elif o in ("-o", "--output"):
            outputPath = a
        elif o in ("-r", "--rules"):
            rulesPath = a

    if inputPath is None or outputPath is None or rulesPath is None:
        raise Exception('Pleas specify input, output and rules file')
        # TODO alternatively read from stdin

    evaluate(inputPath, outputPath, rulesPath)

##
# Execute the queries on the given local model and write it to the output
def evaluate(inputPath, outputPath, rulesPath):
    inputUri = 'file:' + inputPath
    model = RDF.Model()
    ttlParser = RDF.TurtleParser()
    ttlParser.parse_into_model(model, inputUri)
    with open (rulesPath, 'r') as rulesFile:
        # just run each query once for now
        queryString = rulesFile.read()
        query = RDF.SPARQLQuery(queryString)
        result = query.execute(model)
        model.add_statements(result.as_stream())

        namespaces = ttlParser.namespaces_seen()
        ttlSerializer = RDF.Serializer(name="turtle")
        for prefix, uri in namespaces.items():
            ttlSerializer.set_namespace(prefix, uri)

        ttlSerializer.serialize_model_to_file(outputPath, model)
        sys.stderr.write("done\n")

def usage():
    print("""
Please use the following options:
    -i  --input     The input model on which the rules will be executed
    -o  --output    The path to where the output will be written
    -r  --rules     The file containing the rule to execute

    Currently only one rule can be executed at a time. For executing multiple rules please run this script multiple times.
""")

if __name__ == "__main__":
    main(sys.argv[1:])
