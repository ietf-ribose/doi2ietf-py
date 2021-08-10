# doi2ietf: Convert DOI metadata into BibXML

[![test](https://github.com/ietf-ribose/doi2ietf-py/actions/workflows/test.yml/badge.svg)](https://github.com/ietf-ribose/doi2ietf-py/actions/workflows/test.yml)
[![release](https://github.com/ietf-ribose/doi2ietf-py/actions/workflows/release.yml/badge.svg)](https://github.com/ietf-ribose/doi2ietf-py/actions/workflows/release.yml)

## Purpose

`doi2ietf` allows you to fetch bibliographic data from a DOI entry and convert
that into IETF BibXML. IETF BibXML is the bibliographic data XML schema used by
IETF RFC XML ([RFC 7991](https://datatracker.ietf.org/doc/html/rfc7991))

The digital object identifier system (DOI) is specified in
[ISO 26324](https://www.iso.org/standard/43506.html) with the Registration
Authority being the
[International Digital Object Identifier Foundation](https://www.doi.org).

The DOI registration authority allows attaching bibliographic metadata on DOI
entries using the CrossRef format, available at https://data.crossref.org, and
`doi2ietf` fetches those metadata from that site.

DOI identifiers can be resolved at the [DOI resolver page](https://dx.doi.org).

NOTE: [doilit](https://github.com/cabo/kramdown-rfc2629/blob/master/bin/doilit)
was originally written by
[Carsten Bormann](https://www.informatik.uni-bremen.de/~cabo/) as part of the
[`kramdown-rfc2629`](https://github.com/cabo/kramdown-rfc2629) package.
The `doi2ietf` package provides the Python equivalent of that functionality.

## Prerequisites

This software requires Python 3.6+.

All dependencies are specified in `setup.py` for PyPA.

## Install

The package is published at PyPi and can be installed on its own.

```sh
pip install doi2ietf
```

## Usage

### Command-line interface

The `doi2ietf` command takes a list of arguments like this:

```sh
doi2ietf [options] [one or more DOI identifiers]
```

Where:

* A DOI identifier looks like this: e.g. `10.1109/5.771073`.
* The list of DOI identifiers have to be be separated by spaces.
* By default, the output is in YAML format, printed to `STDOUT`.

Options include:

* `-x` or `--xml`: produce XML output instead of YAML.
* `-c` or `--cache`: Cache HTTP-requests to `data.crossref.org`.

Example:

```sh
$ doi2ietf -c -x 10.1109/5.771073 10.1109/MIC.2012.29
<reference anchor="a"><front><title>Toward unique identifiers...
<reference anchor="b"><front><title>CoAP: An Application Protocol...
```

### Library

The main function provided by the `doi2ietf` library is `process_doi_list`.

It can be used in the following manner, for example:

```sh
$ python
>>> import doi2ietf
>>> doi2ietf.process_doi_list(['10.1109/5.771073'])
a:
  author:
  - ins: N. Paskin
    name: N. Paskin
  date: 1999-07
  seriesinfo:
    DOI: 10.1109/5.771073
    Proceedings of the IEEE: vol. 87, no. 7, pp. 1208-1227
  title: Toward unique identifiers
>>> doi2ietf.process_doi_list(['10.1109/5.771073'],True)
<reference anchor="a"><front><title>Toward unique identifiers</title>...
```

`process_doi_list` takes the following arguments:

* list of DOI identifiers as strings
* output as XML, a Boolean value (`True` for XML, `False` for YAML as default)
* stream output handle, by default it writes to `sys.stdout`.

## Development

### General

Development using `pyenv` is strongly encouraged.

```sh
virtualenv venv
pip install -e .
```

Dependencies are listed inside `setup.py`.

### Testing

TODO: to change to PyTest.

To test and compare results you can use additional script
`test/test_results.py`.

Before start you need to edit and save config. Copy `config.py.sample` to
`config.py` and edit values. At least you should write correct path to `doilit`
at `path_to_ruby_doilit` variable. If this script not available, you can test
and compare values saved at `path_to_test_output_dir`.

To fetch new values via the Ruby `doilit` script you need to use `-nc` or
`--no-cache` option:

```sh
./test/test_results.py -nc
```
