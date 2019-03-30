#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup fixtures.

NOTE: this script tests uses static method menu.Menu.safe_read_yaml() and function
validators._determine_schema_type, but they are both tested in their respective sections. So Exceptions will be
raised here before those tests run, redundantly, but they're in both places to ensure 100% coverage

NOTE ON YAML FILES NAMING CONVENTION in tests/data:
Files can be added but their name must contain the word 'multiple' or 'single', not both (and they must correspond
to multiple or single schemas)
If a yaml is 'single', it must have 'with_key' or 'without_key' indicating whether it has the top level key 'tabs'
Other than that, yaml files can contain other words to differentiate them or multiply them in future tests
This naming convention is used to test validators_.determine_schema_type()

LIST ON CONFIG FIXTURES:
This conftest.py produces the following fixtures containing config dicts out of .yaml files in tests/data:
1. input_config_dict: all dicts from .yaml files
2. input_config_dict_and_id: tuple of (dict, id) from all .yaml, only to test validators._determine_schema_type()
3. input_config_multiple_only: all dicts from .yaml files which return 'multiple' from 
   validators._determine_schema_type()
4. input_config_single_with_key_only: all dicts from .yaml files which return 'single_with_key' from 
   validators._determine_schema_type()
5. input_config_single_without_key_only: all dicts from .yaml files which return 'single_without_key' from 
   validators._determine_schema_type()
"""

# pylama:ignore=W293,W291,W391,E302,E128 (will be fixed by black)

import os
from pathlib import Path

import pytest
import yaml  # imported due to Menu class dependency

from pysimpletabshellmenu.menu import Menu
from pysimpletabshellmenu.validators import _determine_schema_type

_ = yaml  # just to get rid of pyflakes warning


def yaml_paths():
    """Retrieves paths of input yaml config files used to instantiate the menu.Menu class from tests/data.
    The contents of this folder can be changed without breaking the test suite, as long as they are valid yaml
    with valid schemas.
    """
    path_to_here = Path(os.path.realpath(__file__))
    data_path = path_to_here.parent / "data"
    yaml_paths = [str(x) for x in data_path.glob("*.yaml")]
    return yaml_paths


# precursor for next constants
YAML_PATHS = sorted([path for path in yaml_paths()])

# constants for input_config_dict fixture
YAML_IDS = [os.path.split(os.path.splitext(path)[0])[1] for path in YAML_PATHS]
TEST_CONFIGS = [Menu.safe_read_yaml(path) for path in YAML_PATHS]


def pretest_yaml_ids():
    """Make sure yaml files in /test/data follow naming convention in that folders' README."""
    for yaml_id in YAML_IDS:
        assert yaml_id.find("multiple") != -1 or yaml_id.find("single") != -1
        if yaml_id.find("single") != -1:
            assert yaml_id.find("with_key") != -1 or yaml_id.find("without_key") != -1


pretest_yaml_ids()
print("pretest_yaml_ids test passed")


def pretest_configs_are_dicts():
    """Sanity check, ensure we are passing dicts"""
    for config in TEST_CONFIGS:
        assert isinstance(config, dict)


pretest_configs_are_dicts()
print("pretest_configs_are_dicts passed")


@pytest.fixture(scope="session", params=TEST_CONFIGS, ids=YAML_IDS)
def input_config_dict(request):
    """Returns config dicts of all files in /tests/data to run tests on.
    Since they are session-scoped, they should not be changed by tests."""
    return request.param


@pytest.fixture(scope="function", params=TEST_CONFIGS, ids=YAML_IDS)
def input_config_dict_and_id(request):
    """To test validators._determine_schema_type"""
    return (request.param, YAML_IDS[request.param_index])


def make_type_dict():
    """uses validators._determine_schema_type() to split up configs into separate fixtures.
    Ensures there is at least one of each"""
    type_dict = {}
    for type_ in ["multiple", "single_with_key", "single_without_key"]:
        type_dict[type_] = {"configs": [], "ids": []}
    for config, id_ in zip(TEST_CONFIGS, YAML_IDS):
        type_ = _determine_schema_type(config)
        assert type_ in ["multiple", "single_with_key", "single_without_key"]  # in case new type appears
        type_dict[type_]["configs"].append(config)
        type_dict[type_]["ids"].append(id_)
    for type_ in ["multiple", "single_with_key", "single_without_key"]:
        assert len(type_dict[type_]) > 0
    return type_dict


TYPE_DICT = make_type_dict()


@pytest.fixture(scope="session", params=TYPE_DICT["multiple"]["configs"], ids=TYPE_DICT["multiple"]["ids"])
def input_config_multiple_only(request):
    """Returns config dicts only if they are the 'multiple' type"""
    return request.param


@pytest.fixture(
    scope="session", params=TYPE_DICT["single_without_key"]["configs"], ids=TYPE_DICT["single_without_key"]["ids"]
)
def input_config_single_without_key_only(request):
    """Returns config dicts only if they are the 'single_without_key' type"""
    return request.param


@pytest.fixture(
    scope="session", params=TYPE_DICT["single_with_key"]["configs"], ids=TYPE_DICT["single_with_key"]["ids"]
)
def input_config_single_with_key_only(request):
    """Returns config dicts only if they are the 'single_with_key' type"""
    return request.param
