#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Contains Menu class; this is the base imported class of this package"""

# pylama:ignore=W293,W291,W391,E302 (will be fixed by black)

import json

import yaml

from . import validators
from . import formatting
from .tab import Tab


class Menu:
    """Base class to import to create a menu

    Contains staticmethods 'safe_read_yaml' and 'read_json' to create expected config dict from config files. Dict's 
    schema is validated before use. (see examples or tests/data directory in repo )

    :param config: nested data structure containing all info used to make menu
    :type config: dict
    """

    def __init__(self, config):
        self.config = config
        # validate config
        validators.validate_all(self.config)
        self._parse_config(self.config)
        self.current_tab_number = 0

    @staticmethod
    def safe_read_yaml(path_to_yaml):
        """Reads yaml file at specified path.

        :param path_to_yaml: path to config yaml file
        :type path_to_yaml: str or pathlib.Path
        :returns: config to pass to instantiate Menu
        :rtype: dict
        """
        with open(path_to_yaml, "r") as f:
            dict_ = yaml.safe_load(f)
        return dict_

    @staticmethod
    def read_json(path_to_json):
        """Reads json file at specified path.

        :param path_to_json: path to config json file
        :type path_to_yaml: str or pathlib.Path
        :returns: config to pass to instantiate Menu
        :rtype: dict
        """
        with open(path_to_json, "r") as f:
            dict_ = json.load(f)
        return dict_

    def _parse_config(self):
        """Creates Tab objects"""
        self.case_sensitive = self.config.get("case_sensitive", False)
        self.screen_width = self.config.get("screen_width", 80)
        if self.config.get("items", None):
            tabs = [{"items": self.config["items"]}]
        else:
            tabs = self.config["tabs"]
        self.tab_selectors = []
        for tab in tabs:
            if tab.get(tab["header_choice_displayed_and_accepted"], None):
                self.tab_selectors.append(tab["header_choice_displayed_and_accepted"])
        if len(self.config["tabs"]) == 1:
            self.headers = False
        else:
            self.headers = True
        self.tabs = []
        for tab in tabs:
            self.tabs.append(Tab(tab, self.tab_selectors, self.case_sensitive))

    def _change_tab(self, new_number):
        # print message about new selection
        old_tab = self.tabs[self.current_tab_number]
        if old_tab.head_choice:
            msg = [f"Change tab to {old_tab.head_choice}"]
            if old_tab.head_desc:
                msg.append(f": {old_tab.head_desc}")
            if old_tab.head_desc_long:
                msg.append(f"\n{old_tab.head_desc_long}")
            print("".join(msg))
        self.current_tab_number = new_number

    def _print_menu(self):
        formatted = formatting.format_menu(self.tabs, self.current_tab_number)
        print(formatted)

    def _collect_input(self):
        received_valid_input = False
        prompt = "?"
        while not received_valid_input:
            selection = input(f"{prompt}: ")  # monkeypatch for testing
            if not self.case_sensitive:
                selection = selection.lower()
            return_dict = self.tabs[self.current_tab_number].process_input(selection)
            if return_dict["type"] == "invalid":
                prompt = "Invalid, try again"
                continue
            else:
                received_valid_input = True
        return return_dict

    def run(self):
        """Called by user, runs menu until valid selection from a tab is made, and returns value
        
        :returns: tuple of tab header choice, return value
        :rtype: (str or None, str)

        Note that the first item in the tuple is None if there is only one tab/are no tabs
        """
        received_return_value = False
        while not received_return_value:
            self._print_menu()
            return_dict = self._collect_input()
            if return_dict["type"] == "change_tab":
                self.change_tab(return_dict["new_number"])
                continue
            else:
                received_return_value = True
                if self.tab_selectors:
                    tab_id = self.tab_selectors[self.current_tab_number]
                else:
                    tab_id = None
        return (tab_id, return_dict["return_value"])
