#!/usr/bin/env python3

""" Filename:     doi2ietf.py
    Purpose:      This file is python port of doilit script
                  (https://github.com/cabo/kramdown-rfc2629/blob/master/bin/doilit)
    Requirements: PyYAML, requests, requests_cache
    Author:
"""

import sys
import argparse
from string import ascii_lowercase

import yaml

import requests

try:
    import requests_cache

    CAN_CACHE = True

except ImportError:

    CAN_CACHE = False

    print("Unable to import requests-cache, caching disabled")

from simplejson.errors import JSONDecodeError


# port https://github.com/cabo/kramdown-rfc2629/blob/master/bin/doilit


HEADERS = {
    "Accept": "application/citeproc+json",
    "User-Agent": "DOI converter"
}


def make_url(doi_id):
    return "https://data.crossref.org/%s" % doi_id


def transform_doi_metadata(data):
    result = {"seriesinfo": {}}

    result["seriesinfo"]["DOI"] = data["DOI"]

    result["title"] = data["title"]

    if data.get("subtitle", []):
        if "".join(data["subtitle"]):
            result["title"] += ": "
            result["title"] += "; ".join(data["subtitle"])

    result["author"] = author_name(data["author"])

    if "issued" in data:
        _issued = data.get("issued", {})

        for _elm in _issued.get("date-parts", []):
            if isinstance(_elm[0], int):
                result["date"] = "%04d" % _elm[0]

                for _i in _elm[1:]:
                    result["date"] += "-%02d" % _i

    if data.get("container-title", False):
        ct = data.get("container-title")
        info = []
        if data.get("volume", False):
            vi = "vol. %s" % data.get("volume")

            if data.get("journal-issue", False):
                if data["journal-issue"].get("issue", False):
                    vi += ", no. %s" % data["journal-issue"]["issue"]

            info.append(vi)

        if data.get("page", False):
            info.append("pp. %s" % data["page"])

        if info:
            result["seriesinfo"][ct] = ", ".join(info)
        else:
            # https://github.com/cabo/kramdown-rfc2629/blob/d006536e2bab3aa9b8a70464710a725ca98a3051/bin/doilit#L91
            # very strange and unsafe, need explaination:
            spl = ct.split(" ")

            result["seriesinfo"][" ".join(spl[0:-1])] = spl[-1]
    elif data.get("publisher", False):
        info = []
        publisher = data["publisher"]
        if data.get("type", False):
            info.append(data["type"])

        if info:
            result["seriesinfo"][publisher] = ", ".join(info)
        else:
            # https://github.com/cabo/kramdown-rfc2629/blob/d006536e2bab3aa9b8a70464710a725ca98a3051/bin/doilit#L104
            # very strange and unsafe, need explaination:
            spl = publisher.split(" ")
            result["seriesinfo"][" ".join(spl[0:-1])] = spl[-1]

    return result


def author_name(authors):
    result = []

    for author in authors:
        _affiliation = author.get("affiliation", None)
        _family = author.get("family", None)
        _given = author.get("given", None)
        _sequence = author.get("sequence", None)

        if _family and _given:
            result.append(
                {
                    "name": "%s %s" % (_given, _family),
                    "ins": "%s. %s" % (_given[0:1], _family),
                }
            )
        else:
            result.append({"name": _family})

    return result


def parse_doi_list(lst):
    i = 0

    for doi_id in lst:
        doi_url = make_url(doi_id)

        json_data = None

        try:
            req = requests.get(doi_url, headers=HEADERS)
        except:
            pass

        try:
            json_data = req.json()

        except JSONDecodeError:
            print("Unable to decode response from: %s " % doi_url)

        if json_data:
            json_data = transform_doi_metadata(json_data)

            yaml.safe_dump(
                # ascii enumerate:
                {ascii_lowercase[i]: json_data},
                sys.stdout,
                allow_unicode=True,
                default_flow_style=False
            )
        i += 1


PARSER = argparse.ArgumentParser(description="DOI 2 IETF converter")
PARSER.add_argument(
    "doi_id_list",
    metavar="N",
    type=str,
    nargs="+",
    help="an integer for the accumulator",
)

PARSER.add_argument(
    "-c",
    "--cache",
    dest="use_cache",
    action="store_true",
    help="Use cache for HTTP-requests",
)


ARGS = PARSER.parse_args()

if ARGS.use_cache:
    if CAN_CACHE:
        with requests_cache.enabled():
            parse_doi_list(ARGS.doi_id_list)
    else:
        print("Need installed requests-cache module for caching HTTP requests")

else:
    parse_doi_list(ARGS.doi_id_list)
