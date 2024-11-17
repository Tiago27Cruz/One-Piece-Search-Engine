#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path


import requests

sagas = ["east blue saga", "alabasta aaga", "sky island saga", "water 7 saga", "thriller bark saga",
          "summit war saga", "fish-man island saga", "dressrosa saga", "whole cake island saga", "wano country saga", "final saga"]


def fetch_solr_results(query, collection, params, solr_uri):
    """
    Fetch search results from a Solr instance based on the query parameters.

    Arguments:
    - query_file: Path to the JSON file containing Solr query parameters.
    - solr_uri: URI of the Solr instance (e.g., http://localhost:8983/solr).
    - collection: Solr collection name from which results will be fetched.

    Output:
    - Prints the JSON search results to STDOUT.
    """

    # Construct the Solr request URL
    uri = f"{solr_uri}/{collection}/select"

    try:
        # Send the POST request to Solr

        bq = ""

        if params == "params":
            for saga in sagas:
                if saga.lower() in query.lower():
                    if bq != "":
                        bq += " OR "
                    bq += "Saga:\""+saga+"\"^50"
        
        solr_params = {
            "q": query,
            "fl": "id, Episode, score",
            "useParams": params,
            "bq": bq
        }

        response = requests.post(uri, params=solr_params, headers={"Content-Type": "application/x-www-form-urlencoded"})
        response.raise_for_status()  # Raise error if the request failed
    except requests.RequestException as e:
        print(f"Error querying Solr: {e}")
        sys.exit(1)

    # Fetch and print the results as JSON
    results = response.json()
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    # Set up argument parsing for the command-line interface
    parser = argparse.ArgumentParser(
        description="Fetch search results from Solr and output them in JSON format."
    )

    # Add arguments for query file, Solr URI, and collection name
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Query",
    )
    parser.add_argument(
        "--collection",
        type=str,
        required=True,
        help="Collection",
    )
    parser.add_argument(
        "--useParams",
        type=str,
        required=True,
        help="Params",
    )
    parser.add_argument(
        "--uri",
        type=str,
        default="http://localhost:8983/solr",
        help="The URI of the Solr instance (default: http://localhost:8983/solr).",
    )

    # Parse command-line arguments
    args = parser.parse_args()

    # Call the function with parsed arguments
    fetch_solr_results(args.query, args.collection, args.useParams, args.uri)
