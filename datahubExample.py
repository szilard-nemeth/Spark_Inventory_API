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
arg_parse = ArgParse(DEFAULT_CONFIG)
args = arg_parse.do_parse()
config = Config(filename=args.config)

client = SparkHistoryClient(config.base_url(),
                            config.knox_token(allow_empty=not config.pass_token()),
                            config.pass_token(),
                            15)

apps = client.list_applications(status="completed", limit=100)

for app in apps:
    appId = app['id']
    print(f"\nSpark App ID: {appId}")

    # Spark apps always have at least one attempt entry in the 'attempts' list
    for attempt in app.get('attempts', []):
        # Extract the actual attemptId from the metadata
        # IMPORTANT: Do not default to "1" or an index if it's missing
        actual_attempt_id = attempt.get('attemptId')

        if actual_attempt_id:
            print(f"Spark Attempt ID: {actual_attempt_id}")
            env_info = client.get_environment(appId, actual_attempt_id)
        else:
            print("No specific Attempt ID found (using base application environment)")
            # If your SparkHistoryClient.py allows it, pass None or handle the path change
            # Most clients need a slight adjustment to handle the missing ID
            env_info = client.get_environment(appId, None)

        spark_props = env_info.get("sparkProperties", [])
        for key, value in spark_props:
            print(f"{key}: {value}")