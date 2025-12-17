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

import requests
import pandas as pd
from typing import Any, Dict, List, Optional

class SparkHistoryClient:
    def __init__(self, base_url: str, cdp_token: str, pass_token, timeout: float = 10.0):
        """
        :param base_url: e.g. https://spark-cluster-arm-gateway.pdf-jul2.a465-9q4k.cloudera.site/spark-cluster-arm/cdp-proxy/spark3history
        :param timeout: HTTP timeout in seconds
        :param cdp_token: obtain from Knox Token Management UI
        """
        self.base_url = base_url
        self.timeout = timeout
        self.cdp_token = cdp_token
        self._pass_token = pass_token
        if not self._pass_token:
            print("Not passing KNOX token as per configuration!")

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        cookies = {}
        if self._pass_token:
            cookies = {
                'hadoop-jwt': self.cdp_token,
            }

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        url = f"{self.base_url}/api/v1{path}"
        resp = requests.get(url, params=params, timeout=self.timeout, headers=headers, cookies=cookies)
        resp.raise_for_status()
        return resp.json()

    def list_applications(self, status: str = None,
                          min_date: str = None, max_date: str = None,
                          min_end_date: str = None, max_end_date: str = None,
                          limit: int = None) -> List[Dict]:
        """
        List applications with optional filters. Date format: ISO or epoch milliseconds.
        """
        params = {}
        for k, v in [
            ('status', status),
            ('minDate', min_date),
            ('maxDate', max_date),
            ('minEndDate', min_end_date),
            ('maxEndDate', max_end_date),
            ('limit', limit)
        ]:
            if v is not None:
                params[k] = v
        return self._get('/applications', params)

    def get_jobs(self, app_id: str) -> List[Dict]:
        return self._get(f'/history/{app_id}/jobs')

    def get_stages(self, app_id: str) -> List[Dict]:
        return self._get(f'/history/{app_id}/stages')

    #def get_stage_attempt(self, app_id: str, stage_id: int, attempt_id: int) -> Dict:
    #    return self._get(f'/applications/{app_id}/stages/{stage_id}/{attempt_id}')

    def get_executors(self, app_id: str) -> List[Dict]:
        return self._get(f'/applications/{app_id}/executors')

    def get_environment(self, app_id, attempt_id=None):
        if attempt_id:
            path = f"/applications/{app_id}/{attempt_id}/environment"
        else:
            path = f"/applications/{app_id}/environment"

        return self._get(path)

    def get_environment_base(self, app_id: str) -> Dict:
        """
        Retrieves Spark submit environment info, including Spark submit options.
        """
        return self._get(f"/applications/{app_id}/environment")

    def get_logs(self, app_id: str, attempt_id: Optional[int] = None) -> Any:
        suffix = f"/{attempt_id}" if attempt_id else ""
        return self._get(f'/applications/{app_id}{suffix}/logs')

    def get_task_summary(self, app_id: str, stage_id: int, attempt_id: int) -> Dict:
        return self._get(f'/applications/{app_id}/stages/{stage_id}/{attempt_id}/taskSummary')

    def get_task_list(self, app_id: str, stage_id: int, attempt_id: int) -> List[Dict]:
        return self._get(f'/applications/{app_id}/stages/{stage_id}/{attempt_id}/taskList')

    def getAllAppMetadata(self, apps):
        """Method to scrape all metadata for all apps including ID, Spark Properties and Resource Profiles"""

        allAppMetadata = {}

        for app in apps:
            appId = app['id']
            env_info = self.get_environment_base(appId)
            allAppMetadata[appId] = appId
            appMetadata = {
                "sparkProperties": env_info.get("sparkProperties"),
                "resourceProfiles": env_info.get("resourceProfiles")
            }

            allAppMetadata[appId] = appMetadata

        return allAppMetadata

    def buildMetadataDf(self, allAppMetadata):
        """Method to flatten and create a pandas df with all filtered metadata from all apps"""

        # Build flat rows
        flattened_rows = []

        for app_id, content in allAppMetadata.items():
            row = {'app_id': app_id}

            # Flatten sparkProperties (key-value pairs)
            for key, value in content.get('sparkProperties', []):
                row[key] = value

            # Process each resource profile
            for profile in content.get('resourceProfiles', []):
                for section, resources in profile.items():
                    if isinstance(resources, dict):
                        for res_key, res_val in resources.items():
                            if isinstance(res_val, dict):
                                resource_name = res_val.get('resourceName')
                                amount = res_val.get('amount')
                                if resource_name is not None and amount is not None:
                                    # Build column name based on the section (e.g. executor_memory)
                                    col_name = f"{section.rstrip('Resources')}_{resource_name}"

                                    if col_name not in row:
                                        row[col_name] = amount
                                    else:
                                        # Handle multiple values
                                        existing = row[col_name]
                                        try:
                                            row[col_name] = float(existing) + float(amount)
                                        except (ValueError, TypeError):
                                            if not isinstance(existing, list):
                                                row[col_name] = [existing]
                                            row[col_name].append(amount)

            flattened_rows.append(row)

        # Create DataFrame
        df = pd.DataFrame(flattened_rows)

        # Use errors='ignore' to prevent KeyError if "id" isn't in the columns
        df = df.drop("id", axis=1, errors='ignore')

        # Return result
        return df
