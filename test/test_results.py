#!/usr/bin/env python3

""" Filename:     test_results.py
    Purpose:      Tool for compare output of doi2ietf.py and doilit

    Requirements: PyYAML, xmldiff, lxml
    Author:
"""

# def test_uppercase():
#     assert "loud noises".upper() == "LOUD NOISES"

import argparse
import subprocess
from pathlib import Path

import yaml

from xmldiff import main
from xmldiff.actions import MoveNode

import lxml.etree as et

from config import (
    path_to_doi2ietf,
    path_to_ruby_doilit,
    path_to_test_output_dir,
    doi_list,
)


def run_shell_script(cmd, args):
    Path(path_to_test_output_dir).mkdir(parents=True, exist_ok=True)

    if "/" not in cmd:
        cmd = "%s/%s" % (Path.cwd(), cmd)
    _cmd = [cmd] + args

    result = subprocess.run(_cmd, stdout=subprocess.PIPE)

    return result


def read_file(path):
    result = None
    with open(path, "rb") as file:
        result = file.read()
    return result

def write_file(path, data):
    with open(path, "w") as file:
        file.write(data.decode("utf-8"))


def et_to_str(node, xml_declaration=True):
    return et.tostring(
        node,
        xml_declaration=xml_declaration,
        pretty_print=True,
        encoding="utf-8"
    )


def get_python_results(lst, mode="yaml"):
    args = lst.copy()

    if mode == "xml":
        args.append("-x")

    args.append("-c")

    output = run_shell_script(path_to_doi2ietf, args)

    if mode == "xml":
        result = (
            b'<?xml version="1.0" encoding="UTF-8"?><root>'
            + output.stdout
            + b"</root>"
        )
    else:
        result = output.stdout

    return result


def get_ruby_results(lst, mode="yaml"):
    args = lst.copy()

    if mode == "xml":
        args.append("-x=xmlhandle")

    output = run_shell_script(path_to_ruby_doilit, args)

    if mode == "xml":
        result = (
            b'<?xml version="1.0" encoding="UTF-8"?><root>'
            + output.stdout
            + b"</root>"
        )
    else:
        result = output.stdout

    result = result

    return result


def yaml_as_dict(yaml_str):
    my_dict = {}
    docs = yaml.safe_load_all(yaml_str)
    for doc in docs:
        for key, value in doc.items():
            my_dict[key] = value
    return my_dict


def normalize_yaml_str(yaml_str):
    return yaml.dump(yaml.load(yaml_str, yaml.FullLoader)).encode("utf-8")


def compare(use_doilit_cache=True):

    yaml_from_python = get_python_results(doi_list)
    dict_from_python = yaml_as_dict(yaml_from_python)

    write_file(
        "%s/doi2ietf.raw.yaml" % path_to_test_output_dir,
        yaml_from_python,
    )
    write_file(
        "%s/doi2ietf.yaml" % path_to_test_output_dir,
        normalize_yaml_str(yaml_from_python),
    )

    if use_doilit_cache:
        yaml_from_ruby = read_file("%s/doilit.yaml" % path_to_test_output_dir)
        dict_from_ruby = yaml_as_dict(yaml_from_ruby)
    else:
        yaml_from_ruby = get_ruby_results(doi_list)
        dict_from_ruby = yaml_as_dict(yaml_from_ruby)
        write_file(
            "%s/doilit.raw.yaml" % path_to_test_output_dir,
            yaml_from_ruby,
        )

        write_file(
            "%s/doilit.yaml" % path_to_test_output_dir,
            normalize_yaml_str(yaml_from_ruby),
        )

    if dict_from_python == dict_from_ruby:
        print("YAML results is identical\n")
    else:
        print("YAML results is NOT identical\n")

    if use_doilit_cache:
        xml_from_ruby = read_file("%s/doilit.xml" % path_to_test_output_dir)
    else:
        xml_from_ruby = get_ruby_results(doi_list, "xml")

    xml_from_python = get_python_results(doi_list, "xml")

    parser = et.XMLParser(remove_blank_text=True)

    ruby_root = et.fromstring(xml_from_ruby, parser)
    python_root = et.fromstring(xml_from_python, parser)

    if not use_doilit_cache:
        write_file(
            "%s/doilit.xml" % path_to_test_output_dir, et_to_str(ruby_root)
        )

    write_file(
        "%s/doi2ietf.xml" % path_to_test_output_dir, et_to_str(python_root)
    )

    xml_diff_result = main.diff_texts(xml_from_ruby, xml_from_python)

    show_diff_title = False

    for i in xml_diff_result:
        # exclude MoveNode diff - we don't care about elements order
        if not isinstance(i, MoveNode):
            if not show_diff_title:
                show_diff_title = True

            else:
                print("XML diffirence:")
                show_diff_title = False

            # cut <root>:
            node_path = "." + i.node[5:]
            elm = ruby_root.find(node_path)

            print("----------------")
            print("XML element (from doilit):", et_to_str(elm, False))
            print(i)
            print("----------------")

    if not show_diff_title and xml_diff_result:
        print("No significant diffirence found at XML results")
        print("(whitespaces and element order only)")

    elif not xml_diff_result:
        print("XML results is identical")


PARSER = argparse.ArgumentParser(
    description="Tool for compare output of doi2ietf.py and doilit"
)

PARSER.add_argument(
    "-nc",
    "--no-cache",
    dest="use_no_cache",
    action="store_true",
    help="Ignore cached results of doilit",
)

ARGS = PARSER.parse_args()

if ARGS.use_no_cache:
    compare(False)
else:
    compare(True)

