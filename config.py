import argparse
import configparser
import os
from collections.abc import Callable

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

    def do_parse(self):
        # 2. Parse the arguments
        args = self.parser.parse_args()
        return args


class Config:
    def __init__(self, filename="config.ini"):
        self.config = configparser.ConfigParser()
        self.config.read(filename)

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