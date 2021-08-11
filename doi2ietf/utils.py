""" Filename:     utils.py
    Purpose:      Recently used functions for python port of "doilit" ruby script.
                  (https://github.com/cabo/kramdown-rfc2629/blob/master/bin/doilit)
    Requirements: PyYAML, requests
    Author:       Ribose
"""

import sys

from string import ascii_lowercase
from calendar import month_name
from xml.sax.saxutils import escape
from simplejson.errors import JSONDecodeError

import yaml
import requests


HEADERS = {
    "Accept": "application/citeproc+json",
    "User-Agent": "doi2ietf-py"
}


def make_url(doi):
    # returns url of API endpoint for DOI
    return "https://data.crossref.org/%s" % doi


def make_date_attrs(date_str):
    year = None
    month = None
    day = None

    if '-' in date_str:
        _date = date_str.split('-')
        year = _date[0]

        if len(_date) > 1:
            month = month_name[int(_date[1])]
            if len(_date) > 2:
                day = _date[2]

    elif date_str.isdigit():
        year = date_str

    date_attr = ''
    if year:
        date_attr += ' year="%s"' % year
    if month:
        date_attr += ' month="%s"' % month
    if day:
        date_attr += ' day="%s"' % day

    date_attr = date_attr.strip()

    return date_attr


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
            # very strange and unsafe, need explanation:
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
            # very strange and unsafe, need explanation:
            spl = publisher.split(" ")
            result["seriesinfo"][" ".join(spl[0:-1])] = spl[-1]

    return result


def make_xml(data):
    # Convert dict to XML string as it doing at:
    # https://github.com/cabo/kramdown-rfc2629/blob/d006536e2bab3aa9b8a70464710a725ca98a3051/lib/kramdown-rfc/refxml.rb#L14
    output = ''

    for ref in data:
        output += '<reference anchor="%s">' % ref
        output += '<front>'
        output += '<title>'
        output += escape(data[ref]['title'])
        output += '</title>'
        for author in data[ref]['author']:
            if 'ins' in author:
                output += '<author '
                output += 'initials="%s" surname="%s" fullname="%s">' % (
                    escape(author['ins'][0:2]),
                    escape(author['ins'][2:]).strip(),
                    escape(author['name'])
                )

            else:
                # https://github.com/cabo/kramdown-rfc2629/blob/d006536e2bab3aa9b8a70464710a725ca98a3051/lib/kramdown-rfc/refxml.rb#L50
                # do we need to copy that "heuristic" method?
                output += '<author surname="%s">' % (
                    escape(author['name'])
                )

            # organization empty: because input field is always empty
            output += '<organization></organization>'
            output += '</author>'

        date_attr = make_date_attrs(data[ref]['date'])

        if date_attr:
            output += '<date %s/>' % date_attr

        output += '</front>'

        for name in data[ref]['seriesinfo']:
            output += '<seriesInfo name="%s" value="%s"/>' % (
                escape(name), (data[ref]['seriesinfo'][name])
            )

        output += '</reference>'

    return output


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


def fetch_doi_data(lst):
    """Gets data by Digital Object Identifier list via API of data.crossref.org

    Args:
        lst: List of DOI.

    Returns:
        List, each element is dict converted from JSON
    """

    json_lst = []

    for doi in lst:
        doi_url = make_url(doi)

        json_data = None

        try:
            req = requests.get(doi_url, headers=HEADERS)

        except requests.exceptions.RequestException as err:
            print("Unable to get %s" % doi_url)
            print(err)

            # raise SystemExit(err) ?

        else:
            try:
                json_data = req.json()

            except JSONDecodeError:
                print("Unable to decode response from: %s " % doi_url)

                # raise SystemExit(err) ?

            if json_data:
                json_lst.append(json_data)

    return json_lst


def parse_doi_data(data_lst, xml_output=False):
    """Gets list of dicts with DOI metadata and converts it YAML or BibXML

    Args:
        data_lst: List of dicts with DOI metadata.
        xml_output: Flag used if BibXML output requested.

    Returns:
        List of strings, each element is YAML or BibXML (depends on xml_output)
    """

    i = 0
    output = []

    for doi_data in data_lst:

        # ascii enumerate, as it made at original doilit:
        doi_dict = {
            ascii_lowercase[i]: transform_doi_metadata(doi_data)
        }

        i += 1

        if xml_output:
            output.append(make_xml(doi_dict))
        else:
            output.append(
                yaml.safe_dump(
                    doi_dict,
                    allow_unicode=True,
                    default_flow_style=False
                )
            )

    return output


def process_doi_list(lst, xml_output=False):
    """Gets data by Digital Object Identifier list via API of data.crossref.org

    Args:
        lst: List of DOI.
        xml_output: Flag used if BibXML output requested.

    Returns:
        List of strings, each element is YAML or BibXML (depends on xml_output)
    """

    data_lst = fetch_doi_data(lst)

    return parse_doi_data(data_lst, xml_output)


def output_doi_data(lst, destination=sys.stdout):
    """Outputs result of process_doi_list to "destination" handler

    Args:
        lst: List of strings to output.
        destination: Output handler.
    """

    for doi_data in lst:
        print(doi_data, file=destination)


def handle_cli_call(lst, xml_output=False, destination=sys.stdout):
    """Gets arguments form CLI interface and pass it to process_doi_list(),
       then pass results to output_doi_data()

    Args:
        data_lst: List of dicts with DOI metadata.
        xml_output: Flag used if BibXML output requested.
        destination: Output handler.

    Returns:
        None, output will be passed to "destination" handler
    """

    doi_data = process_doi_list(lst, xml_output)
    output_doi_data(doi_data, destination)
