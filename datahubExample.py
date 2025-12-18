#****************************************************************************
# (C) Cloudera, Inc. 2020-2025
#  All rights reserved.
#
#  Applicable Open Source License: GNU Affero General Public License v3.0
#
#  NOTE: Cloudera open source products are modular software products
#  made up of hundreds of individual components, each of which was
#  individually copyrighted.  Each Cloudera open source product is a
#  collective work under U.S. Copyright Law. Your license to use the
#  collective work is as provided in your written agreement with
#  Cloudera.  Used apart from the collective work, this file is
#  licensed for your use pursuant to the open source license
#  identified above.
#
#  This code is provided to you pursuant a written agreement with
#  (i) Cloudera, Inc. or (ii) a third-party authorized to distribute
#  this code. If you do not have a written agreement with Cloudera nor
#  with an authorized and properly licensed third party, you do not
#  have any rights to access nor to use this code.
#
#  Absent a written agreement with Cloudera, Inc. (“Cloudera”) to the
#  contrary, A) CLOUDERA PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY
#  KIND; (B) CLOUDERA DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED
#  WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT LIMITED TO
#  IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND
#  FITNESS FOR A PARTICULAR PURPOSE; (C) CLOUDERA IS NOT LIABLE TO YOU,
#  AND WILL NOT DEFEND, INDEMNIFY, NOR HOLD YOU HARMLESS FOR ANY CLAIMS
#  ARISING FROM OR RELATED TO THE CODE; AND (D)WITH RESPECT TO YOUR EXERCISE
#  OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, CLOUDERA IS NOT LIABLE FOR ANY
#  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR
#  CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO, DAMAGES
#  RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF
#  BUSINESS ADVANTAGE OR UNAVAILABILITY, OR LOSS OR CORRUPTION OF
#  DATA.
#
# #  Author(s): Paul de Fusco
#***************************************************************************/

from SparkHistoryClient import SparkHistoryClient
from config import Config, ArgParse

DEFAULT_CONFIG = "config_datahub.ini"

def main():
    arg_parse = ArgParse(DEFAULT_CONFIG)
    args = arg_parse.do_parse()
    # print(args.print)
    config = Config(filename=args.config, print_flags=args.print)
    print(f"Config: {config.__dict__}")

    client = SparkHistoryClient(config.base_url(),
                                config.knox_token(allow_empty=not config.pass_token()),
                                config.pass_token(),
                                15)

    apps = client.list_applications(status="completed", limit=100)

    if "printall" in config.print_flags:
        print(f"Apps: {apps}")

    for app in apps:
        appId = app['id']
        print(f"\nSpark App ID: {appId}")

        # Spark apps always have at least one attempt entry in the 'attempts' list
        for attempt in app.get('attempts', []):
            # Extract the actual attemptId from the metadata
            # IMPORTANT: Do not default to "1" or an index if it's missing
            actual_attempt_id = attempt.get('attemptId')
            if "printenv" in config.print_flags:
                _print_env_info(client, appId, actual_attempt_id)
            if "printall" in config.print_flags:
                _print_all(appId, client)

        if "printmeta" in config.print_flags:
            _print_app_metadata(apps, client)


def _print_env_info(client: SparkHistoryClient, appId, attempt_id):
    if attempt_id:
        print(f"Spark Attempt ID: {attempt_id}")
        env_info = client.get_environment(appId, attempt_id)
    else:
        print("No specific Attempt ID found (using base application environment)")
        # If your SparkHistoryClient.py allows it, pass None or handle the path change
        # Most clients need a slight adjustment to handle the missing ID
        env_info = client.get_environment(appId, None)

    spark_props = env_info.get("sparkProperties", [])
    for key, value in spark_props:
        print(f"{key}: {value}")


def _print_app_metadata(apps: list[dict], client: SparkHistoryClient):
    # Get raw metadata for each spark app
    allAppsMetadata = client.getAllAppMetadata(apps)

    # Create Pandas DF from raw app metadata
    metadataDf = client.buildMetadataDf(allAppsMetadata)

    # Show Pandas DF
    print(metadataDf)


def _print_all(appId, client: SparkHistoryClient):
    jobs = client.get_jobs(appId)
    print(f"jobs: {jobs}")

    stages = client.get_stages(appId)
    print(f"stages: {stages}")

    executors = client.get_executors(appId)
    print(f"executors: {executors}")

    # Iterate through each stage to get summaries and task details
    for stage in stages:
        stage_id = stage['stageId']
        # Note: stage['attemptId'] refers to the retry attempt of this specific stage
        stg_attempt_id = stage['attemptId']

        # Get Task Summary (Aggregated metrics like min, max, quartiles)
        task_summary = client.get_task_summary(appId, stage_id, stg_attempt_id)
        print(f"--- Stage {stage_id} (Attempt {stg_attempt_id}) Summary ---")
        print(task_summary)

        # Get Task List (Individual data for every task in this stage)
        task_list = client.get_task_list(appId, stage_id, stg_attempt_id)
        print(f"--- Stage {stage_id} Task List ---")
        for task in task_list:
            print(f"Task ID: {task['taskId']} status: {task['status']}")


if __name__ == '__main__':
    main()