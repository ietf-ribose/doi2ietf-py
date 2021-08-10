from string import ascii_lowercase
from calendar import month_name
from xml.sax.saxutils import escape
from simplejson.errors import JSONDecodeError

import yaml
import requests
import sys

HEADERS = {
    "Accept": "application/citeproc+json",
    "User-Agent": "DOI converter"
}

def make_url(doi_id):
    return "https://data.crossref.org/%s" % doi_id


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

# TODO: clean this up
def parse_doi_list(lst, xml_output=False, destination=sys.stdout):
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
            # ascii enumerate:
            doi_dict = {
                ascii_lowercase[i]: transform_doi_metadata(json_data)
            }

            if xml_output:
                print(make_xml(doi_dict))
            else:
                yaml.safe_dump(
                    doi_dict,
                    destination,
                    allow_unicode=True,
                    default_flow_style=False
                )
        i += 1
