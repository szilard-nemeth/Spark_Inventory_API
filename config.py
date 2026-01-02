import argparse
import configparser
import os
from collections.abc import Callable
from typing import List


class ArgParse:
    def __init__(self, default_config):
        # 1. Set up the Argument Parser
        self.parser = argparse.ArgumentParser(description="Spark History Client Script")
        self.parser.add_argument(
            "--config",
            type=str,
            default=default_config, # Fallback default
            help="Path to the configuration file (e.g., my_config.ini)"
        )

        self.parser.add_argument(
            "--print",
            nargs='+',
            choices=['printenv', 'printmeta', 'printall'],
            default=['printenv'],
            help="Specify which information to print. Multiple values can be provided."
        )

        self.parser.add_argument(
            "--export-df-to-xls",
            action="store_true",
            default=False,
            help="Whether to export Pandas DF to xls."
        )

        self.parser.add_argument(
            "--format-json",
            action="store_true",
            help="Enable formatted JSON printouts."
        )

    def do_parse(self):
        # 2. Parse the arguments
        args = self.parser.parse_args()
        return args


class Config:
    def __init__(self, filename="config.ini", print_flags: List[str] = None, export_dfs_to_xls: bool = False, format_json=False):
        if not print_flags:
            raise ValueError(f"Invalid print_flags: {print_flags}")
        self.config = configparser.ConfigParser()
        self.config.read(filename)
        self.print_flags: List[str] = print_flags
        self.format_json = format_json
        self.export_dfs_to_xls = export_dfs_to_xls

    def base_url(self, allow_empty=False):
        return self.ensure_config(key='BASE_URL', allow_empty=allow_empty)

    def knox_token(self, allow_empty=False):
        return self.ensure_config(key='KNOX_TOKEN', allow_empty=allow_empty, fallback=Config.knox_token_fallback)

    def pass_token(self, allow_empty=False):
        return Config.string_to_bool(self.ensure_config(key='PASS_TOKEN', allow_empty=allow_empty))


    def ensure_config(self, key, allow_empty=False, fallback: Callable[[None, str]]=None):
        fallback_conf_val = None
        fallback_called = False
        conf_val = self.config['DEFAULT'][key]
        if not conf_val:
            if allow_empty:
                return ""
            if fallback:
                fallback_conf_val = fallback()
                fallback_called = True
            if not conf_val and not fallback_conf_val:
                msg = f"Config is empty for key: {key}"
                if fallback_called:
                    msg += " and fallback also returned empty value!"
                raise ValueError(msg)
            return conf_val if conf_val else fallback_conf_val
        return conf_val

    @staticmethod
    def string_to_bool(s):
        """
        Converts string 'True' or 'False' to a boolean using conditionals.
        """
        if s == 'True':
            return True
        elif s == 'False':
            return False
        else:
            raise ValueError(f"Invalid input: '{s}'. Expected 'True' or 'False'.")

    @staticmethod
    def knox_token_fallback():
        return os.getenv("KNOX_TOKEN", None)
        # return os.environ["KNOX_TOKEN"]