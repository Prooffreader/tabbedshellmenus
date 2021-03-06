#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests menu.py"""

# pylama: ignore=D102
# pylint: disable=C0116,C0330,W0212,C0103

from copy import deepcopy
import json
import os

import pytest

# import from __init__
from pytabby import Menu
import pytabby


def yaml_path():
    """Gets path to test yaml file"""
    path_to_here = os.path.realpath(__file__)
    this_dir = os.path.split(path_to_here)[0]
    return os.path.join(this_dir, "data", "test_config.yaml")


@pytest.mark.smoke
@pytest.mark.run(order=-1)
def test_menu_smoke(config_all):
    """Smoke test to see if menu creation succeeds"""
    _ = Menu(config_all)


@pytest.mark.integration
@pytest.mark.run(order=5)
class TestStaticMethods:
    """Tests the static methods to load data"""

    def test_yaml(self):
        """Loads test yaml and instantiates Menu"""
        _ = self.__class__  # just to get rid of codacy warning, I know, it's stupid
        config = Menu.safe_read_yaml(yaml_path())
        _ = Menu(config)

    def test_json(self, tmpdir):
        """Loads test yaml, converts to json, loads json and instantiates Menu

        Also asserts the two dicts are equal
        """
        _ = self.__class__  # just to get rid of codacy warning, I know, it's stupid
        config_from_yaml = Menu.safe_read_yaml(yaml_path())
        p = tmpdir.mkdir("pytabbytest").join("temp.json")
        p.write(json.dumps(config_from_yaml))
        config_from_json = Menu.read_json(str(p))
        if not config_from_yaml == config_from_json:
            raise AssertionError


@pytest.mark.function
@pytest.mark.run(order=6)
def test_method__change_tab(config_multiple, capsys, random_string):
    """Tests menu._change_tab"""
    c = deepcopy(config_multiple)
    c["tabs"][1]["tab_header_input"] = random_string[:3]
    c["tabs"][1]["tab_header_description"] = random_string[3:7]
    c["tabs"][1]["tab_header_long_description"] = random_string[7:]
    menu = Menu(c)
    if menu._current_tab_number != 0:
        raise AssertionError
    menu._change_tab(1)
    out, _ = capsys.readouterr()
    if menu._current_tab_number != 1:
        raise AssertionError
    for astr in [
        "Change tab to {}".format(random_string[:3]),
        ": {}".format(random_string[3:7]),
        "\n{}".format(random_string[7:]),
    ]:
        if out.find(astr) == -1:
            raise AssertionError


@pytest.mark.breaking
@pytest.mark.run(order=7)
def test_breaking_change_tab(config_single_with_key, config_single_without_key):
    """Should not work because you can't change tabs with single tabs"""
    for conf in (config_single_with_key, config_single_without_key):
        c = deepcopy(conf)
        menu = Menu(c)
        with pytest.raises(IndexError):
            menu._change_tab(1)


@pytest.mark.regression
@pytest.mark.run(order=8)
def test_method_print_menu(config_all, capsys, data_regression):
    """Simple regression test of print output, with and without menu"""
    menu = Menu(config_all)
    data = {}
    menu._print_menu("This is a magic string and that's okay")
    out, _ = capsys.readouterr()
    data["output_with_message"] = out.split("\n")
    menu._print_menu()
    out, _ = capsys.readouterr()
    data["output_without_message"] = out.split("\n")
    if data["output_with_message"] == data["output_without_message"]:
        raise AssertionError("output without message should differ from output with message")
    data_regression.check(data)


@pytest.mark.regression
@pytest.mark.run(order=8)
def test_menu_run_printout_after_change_tab(config_multiple, capsys, data_regression):
    """Simple regression test of print output, with different kinds of message for that tab"""
    menu = Menu(config_multiple)
    menu._testing = "message"
    data = {}
    tab_names = (config_multiple["tabs"][0]["tab_header_input"], config_multiple["tabs"][1]["tab_header_input"])
    for message_type in ["dict", "string", "None"]:
        if message_type == "None":
            message = None
        elif message_type == "string":
            message = "Magic string but that's okay"
        elif message_type == "dict":
            message = {tab_names[0]: "Message 1", tab_names[1]: "Message 2"}
        menu.run(message)
        out_before_change, _ = capsys.readouterr()
        menu._change_tab(1)
        menu.run(message)
        out, _ = capsys.readouterr()
        # test that different tabs give different outputs
        if out_before_change == out:
            raise AssertionError
        data["before_change_" + message_type] = out_before_change.split("\n")
        data["after_change_" + message_type] = out.split("\n")
    if (
        data["before_change_dict"] == data["before_change_string"]
        or data["before_change_dict"] == data["before_change_None"]
        or data["before_change_string"] == data["before_change_None"]
        or data["after_change_dict"] == data["after_change_string"]
        or data["after_change_dict"] == data["after_change_None"]
        or data["after_change_string"] == data["after_change_None"]
    ):
        raise AssertionError
    data_regression.check(data)


@pytest.mark.regression
@pytest.mark.run(order=8)
class TestCollectInput:
    """will monkeypatch the module.input function"""

    def test_method_collect_input_with_valid_input(self, config_all_with_id, data_regression):
        _ = self.__class__  # just to get rid of codacy warning, I know, it's stupid
        conf, id_ = config_all_with_id
        c = deepcopy(conf)
        c["case_sensitive"] = False  # to get 100% coverage
        menu = Menu(c)
        normal = menu._config
        test_input_valid_entry = normal["tabs"][0]["items"][0]["item_inputs"][0]
        data = {}
        pytabby.menu.input = lambda x: test_input_valid_entry
        result = menu._collect_input()
        data["result"] = result
        if id_.find("multiple") != -1:
            test_input_tab = normal["tabs"][1]["tab_header_input"]
            pytabby.menu.input = lambda x: test_input_tab
            result2 = menu._collect_input()
            data["result_multiple"] = result2
        data_regression.check(data)

    def teardown_method(self):
        """Reverts input"""
        _ = self.__class__  # just to get rid of codacy warning, I know, it's stupid
        pytabby.menu.input = input


@pytest.mark.breaking
@pytest.mark.run(order=9)
class TestBreakingCollectInput:
    """Monkeypatches module.input function"""

    def test_break_collect_input(self, config_all, random_string):
        """Tries an invalid input with testing=True so it doesn't go into an infinite loop"""
        _ = self.__class__  # just to get rid of codacy warning, I know, it's stupid
        c = deepcopy(config_all)
        menu = Menu(c)
        # this assumes that random_string is not a valid entry in the config file
        # this is a pretty darn safe assumption
        pytabby.menu.input = lambda x: random_string
        menu._testing = "collect_input"
        result = menu._collect_input()
        if result != "Invalid, try again":
            raise AssertionError

    def teardown_method(self):
        """Reverts input"""
        _ = self.__class__  # just to get rid of codacy warning, I know, it's stupid
        pytabby.menu.input = input


@pytest.mark.integration
@pytest.mark.regression
@pytest.mark.run(order=10)
class TestRun:
    """Monkeypatches module.input function"""

    def test_with_invalid_input(self, config_all, random_string):
        _ = self.__class__  # just to get rid of codacy warning, I know, it's stupid
        c = deepcopy(config_all)
        menu = Menu(c)
        pytabby.menu.input = lambda x: random_string
        menu._testing = "run_invalid"
        result = menu.run()
        if result != "Invalid, try again":
            raise AssertionError

    def test_with_change_tab(self, config_multiple):
        _ = self.__class__  # just to get rid of codacy warning, I know, it's stupid
        c = deepcopy(config_multiple)
        menu = Menu(c)
        normal = menu._config
        test_input = normal["tabs"][1]["tab_header_input"]
        pytabby.menu.input = lambda x: test_input
        menu._testing = "run_tab"
        result = menu.run()
        if result != {"new_number": 1, "type": "change_tab"}:
            raise AssertionError

    def test_with_valid_entry(self, config_all, data_regression):
        _ = self.__class__  # just to get rid of codacy warning, I know, it's stupid
        c = deepcopy(config_all)
        menu = Menu(c)
        normal = menu._config
        test_input = normal["tabs"][0]["items"][0]["item_inputs"][0]
        pytabby.menu.input = lambda x: test_input
        data = {}
        result = menu.run()
        data["result"] = result
        data_regression.check(data)

    def test_fail_dict_message_on_single_tab(self, config_single_with_key):
        _ = self.__class__  # just to get rid of codacy warning, I know, it's stupid
        menu = Menu(config_single_with_key)
        with pytest.raises(ValueError):
            menu.run({"any_key": "any string"})

    def test_fail_invalid_key_dict_message(self, config_multiple):
        _ = self.__class__  # just to get rid of codacy warning, I know, it's stupid
        menu = Menu(config_multiple)
        with pytest.raises(ValueError):
            menu.run({"nonexistent_key_magic_string": "any string"})

    def test_fail_wong_type_message(self, config_multiple):
        _ = self.__class__  # just to get rid of codacy warning, I know, it's stupid
        menu = Menu(config_multiple)
        with pytest.raises(TypeError):
            menu.run({3})

    def teardown_method(self):
        """Reverts input"""
        _ = self.__class__  # just to get rid of codacy warning, I know, it's stupid
        pytabby.menu.input = input
