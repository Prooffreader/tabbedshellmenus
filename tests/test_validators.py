#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pylama:ignore=W293,W291,W391,E302,E128,E127,E303 (will be fixed by black)

from copy import deepcopy

import pytest
# from schema import Schema, Or, Optional

import pysimpletabshellmenu.validators as validators

pytest_plugins = ("regressions",)

def test__determine_schema_type(input_config_dict_and_id):
    """As long as naming convention of test files stated in <root>/tests/data are followed, this should
    pass, and that was tested in conftest.py
    """
    config, id_ = input_config_dict_and_id
    schema_type = validators._determine_schema_type(config)
    assert schema_type in ("multiple", "single_with_key", "single_without_key")
    if schema_type == "multiple":
        assert id_.find("multiple") != -1
    if schema_type.startswith("single"):
        assert id_.find("single") != -1
        if schema_type.endswith("_with_key"):
            assert id_.find("with_key") != -1
        if schema_type.endswith("_without_key"):
            assert id_.find("without_key") != -1

@pytest.mark.skip  # TODO: fix this
def test_regression_ValidSchemas(data_regression):
    """Must stringify because contains schema objects"""
    data = str(validators._ValidSchemas().__dict__)
    data = {"data": data}  # apparently data_regression must use dict
    data_regression.check(data)


def test_schema_is_valid_expect_pass(input_config_dict):
    """ensures each test case passes before making them fail for different reasons"""
    assert validators.schema_is_valid(input_config_dict)


@pytest.mark.parametrize("scenario", ["c['new_header'] = 'something'",
                                      "del c['tabs'][0]['items'][0]['choice_displayed']",
                                      "c['tabs'][0]['items'][0]['valid_entries'] = []"],
                                      ids=['unexpected top level header',
                                             'no tabs.items.choice_displayed',
                                             'tabs.items.valid_entries is empty list'])
def test_some_fail_scenarios_multiple(input_config_multiple_only, scenario):
    """Schema test should catch all of these, which are not exhaustive."""
    c = deepcopy(input_config_multiple_only)
    exec(scenario)
    assert not validators.schema_is_valid(c)


def test_optional_top_level_keys_multiple(input_config_multiple_only):
    """Schema test should catch all of these, which are not exhaustive."""
    c = deepcopy(input_config_multiple_only)
    assert validators.schema_is_valid(c)
    for key, value in [('case_sensitive', True), ('screen_width', 60)]:
        if key in c.keys():
            del c[key]
        else:
            c[key] = value
        assert validators.schema_is_valid(c)
    

def test_optional_long_description_multiple(input_config_multiple_only):
    c = deepcopy(input_config_multiple_only)
    assert validators.schema_is_valid(c)
    


@pytest.mark.parametrize("scenario", ["del c['tabs']", "tab = deepcopy(c['tabs'][0]);c['tabs'].append(tab)"])
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


def test__find_tabs(input_config_dict):
    """Hard to make this non tautological"""
    tabs = validators._find_tabs(input_config_dict)
    assert isinstance(tabs[0]["items"], list)


def test_check_return_value_overlap(input_config_dict):
    """Expect pass on valid input data"""
    validators.check_return_value_overlap(input_config_dict)


def test_check_accepted_input_overlap(input_config_dict):
    """Expect pass on valid input data"""
    validators.check_accepted_input_overlap(input_config_dict)


def test_check_return_value_overlap_fail(input_config_multiple_only):
    """Add a duplicate return value in a tab"""
    c = deepcopy(input_config_multiple_only)
    c["tabs"][0]["items"].append(c["tabs"][0]["items"][-1])
    try:
        validators.check_return_value_overlap(c)
    except AssertionError:
        pass


def test_check_return_value_overlap_fail_within(input_config_multiple_only):
    """Add a duplicate input value within a tab"""
    c = deepcopy(input_config_multiple_only)
    c["tabs"][0]["items"].append(c["tabs"][0]["items"][-1])
    try:
        validators.check_return_value_overlap(c)
        raise AssertionError
    except AssertionError:
        pass


def test_check_return_value_overlap_fail_wtab(input_config_multiple_only):
    """Add another tab input value to a tab input"""
    c = deepcopy(input_config_multiple_only)
    extra_value = c["tabs"][0]["header_choice_displayed_and_accepted"]
    c["tabs"][1]["items"][0]["valid_entries"].append(extra_value)
    try:
        validators.check_return_value_overlap(c)
        raise AssertionError
    except AssertionError:
        pass
