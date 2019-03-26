#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy

import pytest
from schema import Schema, Or, Optional

import pysimpletabshellmenu.validators as validators


def test__determine_schema_type(input_config_dict_and_id):
    """As long as naming convention of test files stated in <root>/tests/data are followed, this should
    pass, and that was tested in conftest.py
    """
    config, id_ = input_config_dict_and_id
    print(id_)
    schema_type = validators._determine_schema_type(config)
    assert schema_type in ("multiple", "single_with_key", "single_without_key")
    assert 1 == 1
    if schema_type == "multiple":
        assert id_.find("multiple") != -1
    if schema_type.startswith("single"):
        assert id_.find("single") != -1
        if schema_type.endswith("_with_key"):
            assert id_.find("with_key") != -1
        if schema_type.endswith("_without_key"):
            assert id_.find("without_key") != -1


def test_regression_ValidSchemas():
    """Simply copies code from validators._ValidSchemas to see if it ever changes"""

    class _ValidSchemasRegression:

        def __init__(self):

            self.outer_schema_multiple_or_single_with_key = Schema(
                {"case_sensitive": bool, Optional("screen_width"): int, "tabs": list}
            )

            self.outer_schema_single_without_key = Schema(
                {"case_sensitive": bool, Optional("screen_width"): int, "items": list}
            )

            self.tab_schema_multiple = Schema(
                {
                    "header_choice_displayed_and_accepted": Or(int, str),
                    "header_description": Or(str, None),
                    "items": list,
                }
            )

            self.tab_schema_single = Schema({"items": list})

            self.item_schema = Schema(
                {
                    "choice_displayed": Or(str, int),
                    "choice_description": str,
                    "valid_entries": list,
                    "returns": Or(str, int),
                }
            )

            self.entry_schema = Schema(Or(int, str))

    current = validators._ValidSchemas()
    regressed = _ValidSchemasRegression()
    assert str(current.__dict__) == str(regressed.__dict__)


def test_schema_is_valid_expect_pass(input_config_dict):
    """ensures each test case passes before making them fail for different reasons"""
    assert validators.schema_is_valid(input_config_dict)


@pytest.mark.parametrize("scenario", [
    "c['new_header'] = 'something'"])
def test_some_fail_scenarios_multiple(input_config_multiple_only, scenario):
    """Schema test should catch all of these, which are not exhaustive."""
    c = deepcopy(input_config_multiple_only)
    exec(scenario)
    assert not validators.schema_is_valid(c)

@pytest.mark.parametrize("scenario", ["del c['tabs']",
                                     "tab = deepcopy(c['tabs'][0]);c['tabs'].append(tab)"
                                     ])
def test_some_fail_scenarios_single_with_key(input_config_single_with_key_only, scenario):
    """Schema test should catch all of these, which are not exhaustive."""
    c = deepcopy(input_config_single_with_key_only)
    exec(scenario)
    assert not validators.schema_is_valid(c)


@pytest.mark.parametrize("scenario", ["c['items'][0]['valid_entries'].append(1.5)"])
def test_some_fail_scenarios_single_without_key(input_config_single_without_key_only, scenario):
    """Schema test should catch all of these, which are not exhaustive."""
    c = deepcopy(input_config_single_without_key_only)
    exec(scenario)
    assert not validators.schema_is_valid(c)
