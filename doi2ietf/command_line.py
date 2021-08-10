#!/usr/bin/env python3

""" Filename:     doi2ietf.py
    Purpose:      This file is python port of doilit script
                  (https://github.com/cabo/kramdown-rfc2629/blob/master/bin/doilit)
    Requirements: PyYAML, requests, requests_cache
    Author:       Ribose
"""

import sys
import argparse
from .utils import parse_doi_list

def main():
    try:
        import requests_cache

        CAN_CACHE = True

    except ImportError:

        CAN_CACHE = False

        print("Unable to import requests-cache, caching disabled")

    PARSER = argparse.ArgumentParser(description="DOI 2 IETF converter")

    PARSER.add_argument(
        "doi_id_list",
        metavar="N",
        type=str,
        nargs="+",
        help="DOI ID",
    )

    PARSER.add_argument(
        "-c",
        "--cache",
        dest="use_cache",
        action="store_true",
        help="Use cache for HTTP-requests",
    )

    PARSER.add_argument(
        "-x",
        "--xml",
        dest="xml_output",
        action="store_true",
        help="Output in XML",
    )

    ARGS = PARSER.parse_args()

    if ARGS.use_cache:
        if CAN_CACHE:
            with requests_cache.enabled():
                parse_doi_list(ARGS.doi_id_list, ARGS.xml_output)
        else:
            print("Need installed requests-cache module for caching HTTP requests")

    else:
        parse_doi_list(ARGS.doi_id_list, ARGS.xml_output, sys.stdout)

if __name__ == "__main__":
    sys.exit(main())
