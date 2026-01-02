import argparse
import configparser
import json
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


class ApplicationDataPrinter:
    def __init__(self, config, client):
        self._config = config
        self._client = client

    def print(self):
        apps = self._client.list_applications(status="completed", limit=100)

        if "printall" in self._config.print_flags:
            print(f"Apps: {self._to_json(apps)}")

        for app in apps:
            appId = app['id']
            print(f"\nSpark App ID: {appId}")

            # Spark apps always have at least one attempt entry in the 'attempts' list
            for attempt in app.get('attempts', []):
                # Extract the actual attemptId from the metadata
                # IMPORTANT: Do not default to "1" or an index if it's missing
                actual_attempt_id = attempt.get('attemptId')
                if "printenv" in self._config.print_flags:
                    self._print_env_info(appId, actual_attempt_id)
                if "printall" in self._config.print_flags:
                    self._print_all(appId)

            if "printmeta" in self._config.print_flags:
                self._print_app_metadata(apps)

    def _print_env_info(self, appId, attempt_id):
        if attempt_id:
            print(f"Spark Attempt ID: {attempt_id}")
            env_info = self._client.get_environment(appId, attempt_id)
        else:
            print("No specific Attempt ID found (using base application environment)")
            # If your SparkHistoryClient.py allows it, pass None or handle the path change
            # Most clients need a slight adjustment to handle the missing ID
            env_info = self._client.get_environment(appId, None)

        spark_props = env_info.get("sparkProperties", [])
        for key, value in spark_props:
            print(f"{key}: {value}")


    def _print_app_metadata(self, apps: list[dict]):
        # Get raw metadata for each spark app
        allAppsMetadata = self._client.getAllAppMetadata(apps)

        # Create Pandas DF from raw app metadata
        metadataDf = self._client.buildMetadataDf(allAppsMetadata)

        # Show Pandas DF
        print(metadataDf)

        if self._config.export_dfs_to_xls:
            metadataDf.to_excel("/home/cdsw/spark_app_summary.xlsx", index=False)

    def _print_all(self, appId):
        jobs = self._client.get_jobs(appId)
        print(f"jobs: {self._to_json(jobs)}")

        stages = self._client.get_stages(appId)
        print(f"stages: {self._to_json(stages)}")

        executors = self._client.get_executors(appId)
        print(f"executors: {self._to_json(executors)}")

        # Iterate through each stage to get summaries and task details
        for stage in stages:
            stage_id = stage['stageId']
            # Note: stage['attemptId'] refers to the retry attempt of this specific stage
            stg_attempt_id = stage['attemptId']

            # Check if the stage actually ran tasks
            # Spark returns 404 on taskSummary if no tasks have finished
            if stage.get('numCompleteTasks', 0) > 0:
                try:
                    task_summary = self._client.get_task_summary(appId, stage_id, stg_attempt_id)
                    print(f"--- Stage {stage_id} Summary ---")
                    print(self._to_json(task_summary))
                except Exception as e:
                    print(f"Skipping summary for Stage {stage_id}: {e}")
            else:
                print(f"Stage {stage_id} has no completed tasks; skipping summary.")

            # Get Task List (Individual data for every task in this stage)
            task_list = self._client.get_task_list(appId, stage_id, stg_attempt_id)
            print(f"--- Stage {stage_id} Task List ---")
            for task in task_list:
                print(f"Task ID: {task['taskId']} status: {task['status']}")

    def _to_json(self, s):
        if self._config.format_json:
            return json.dumps(s, indent=4)
        return json.dumps(s)
