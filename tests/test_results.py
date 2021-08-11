import glob

import json
import yaml

from xmldiff.main import diff_texts as diff_xml_texts
from xmldiff.actions import MoveNode

from doi2ietf.utils import parse_doi_data


FIXTURES_PATH = "fixtures"


def read_fixtures():
    fixtures = {}

    for fname in glob.glob("%s/*.json" % FIXTURES_PATH):
        doi = fname.replace("%2F", "/")[len(FIXTURES_PATH)+1:][:-5]

        if not doi in fixtures:
            fixtures[doi] = {}

        yaml_fname = "%s.yaml" % fname[:-5]
        xml_fname = "%s.xml" % fname[:-5]

        with open(fname, "r", encoding="utf-8") as fhandler:
            fixtures[doi]["json_dict"] = json.load(fhandler)

        with open(yaml_fname, "r", encoding="utf-8") as fhandler:
            fixtures[doi]["yaml_str"] = fhandler.read()

        with open(xml_fname, "r", encoding="utf-8") as fhandler:
            fixtures[doi]["xml_str"] = fhandler.read()

    return fixtures


def yaml_to_dict(yaml_str):
    my_dict = {}
    docs = yaml.safe_load_all(yaml_str)

    for doc in docs:
        for key, value in doc.items():
            my_dict[key] = value
    return my_dict


def normalize_yaml_str(yaml_str):
    return yaml.dump(yaml.load(yaml_str, yaml.FullLoader)).encode("utf-8")


def compare_yaml_str(str_0, str_1):
    yaml_dict_0 = yaml_to_dict(normalize_yaml_str(str_0))
    yaml_dict_1 = yaml_to_dict(normalize_yaml_str(str_1))

    assert (yaml_dict_0 == yaml_dict_1), "Normalized YAML results are not identical"


def compare_xml_str(str_0, str_1):
    xml_diff_result = diff_xml_texts(str_0, str_1)

    for i in xml_diff_result:
        # exclude MoveNode diff - we don't care about elements order
        if not isinstance(i, MoveNode):
            raise AssertionError("Normalized XML results are not identical", i)


def test_results():
    # compare fixtures results with results of parse_doi_data()

    fixtures = read_fixtures()

    for doi in fixtures:

        print("Testing YAML results, DOI %s" % doi)
        yaml_results = parse_doi_data([fixtures[doi]["json_dict"]])
        compare_yaml_str(fixtures[doi]["yaml_str"], yaml_results[0])

        print("Testing XML results, DOI %s" % doi)
        xml_results = parse_doi_data([fixtures[doi]["json_dict"]], True)
        compare_xml_str(fixtures[doi]["xml_str"], xml_results[0])
