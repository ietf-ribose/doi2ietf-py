#!/usr/bin/env python3

""" Filename:     command_line.py
    Purpose:      This file is CLI interface to doi2ietf
    Requirements: requests_cache
    Author:       Ribose
"""

import sys
import argparse

from .utils import handle_cli_call


def main():
    try:
        import requests_cache

        CAN_CACHE = True

    except ImportError:

        CAN_CACHE = False

        print("Unable to import requests-cache, caching disabled")

    PARSER = argparse.ArgumentParser(description="DOI 2 IETF converter")

    PARSER.add_argument(
        "doi_list",
        metavar="DOI",
        type=str,
        nargs="+",
        help="List of DOI",
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
                handle_cli_call(ARGS.doi_list, ARGS.xml_output)
        else:
            print("Need installed requests-cache module for caching HTTP requests")

    else:
        handle_cli_call(ARGS.doi_list, ARGS.xml_output, sys.stdout)


if __name__ == "__main__":
    sys.exit(main())
