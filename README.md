# Spark Inventory API

A Python-based toolkit designed to programmatically interface with the **Spark History Server (SHS) API**. This utility simplifies the process of auditing Spark applications by extracting environment configurations, performance metrics, and resource profiles into readable console outputs or structured Excel reports.

## Features

* **Automated Data Retrieval**: Fetches comprehensive data for Applications, Jobs, Stages, and Executors.
* **Environment Auditing**: Extracts and displays `sparkProperties` to verify runtime configurations and tuning.
* **Metadata Flattening**: Automatically flattens nested Spark JSON responses into a single, analysis-ready Pandas DataFrame.
* **Excel Export**: Integrated support for exporting aggregated application metadata to `.xlsx` files.
* **Flexible Authentication**: Supports Knox Token authentication via configuration files or environment variable fallbacks.

---

## Project Structure

* `common.py`: The core orchestration layer containing the `Launcher`, `ArgParse`, and `Config` classes.
* `SparkHistoryClient.py`: The API wrapper that handles HTTP requests, authentication via `hadoop-jwt` cookies, and data transformation.
* `baseExample.py` / `datahubExample.py`: Pre-configured entry point scripts for different environment defaults.

---

## Requirements

* A Python environment.
* A CDP DataHub Public Cloud cluster.

## Prerequisites

Ensure you have Python 3.x installed along with the dependencies defined in `requirements.txt:

```bash
pip install requirements.txt
```


## Configuration
The tool relies on `.ini` files for environment-specific settings.

Configuration Keys (`[DEFAULT]` section in ini file):

| Key          | Description                                                                        |
|--------------|------------------------------------------------------------------------------------|
| `BASE_URL`   | The full URL to your Spark History Server API (e.g., `https«://.../spark3history`) |
| `KNOX_TOKEN` | Your CDP/Knox authentication token.                                                |
| `PASS_TOKEN` | Set to `True` to enable token-based authentication; `False` to ignore.             |

The `BASE_URL` is found in the DataHub Endpoints UI. The `KNOX_TOKEN` must be generated from the DataHub Knox UI.


Example `config_base.ini`, 
```ini
BASE_URL = [https://spark-cluster-gateway.cloudera.site/spark3history](https://spark-cluster-gateway.cloudera.site/spark3history)
KNOX_TOKEN = your_knox_token_here
PASS_TOKEN = True
```

Note: If `KNOX_TOKEN` is empty in the `.ini` config file, the client will look for a `KNOX_TOKEN` environment variable.

## Usage
Run the utility using one of the example scripts. You can use command-line flags to override the configuration or change the output verbosity.

### Basic Execution
```shell
python3 baseExample.py
```

### Advanced Execution with Overrides
```bash
python3 datahubExample.py --config my_custom_config.ini --print printall --format-json --export-df-to-xls
```


### Command Line Arguments

| Argument           | Description                                                          | Default / Choices                                        |
|--------------------|----------------------------------------------------------------------|----------------------------------------------------------|
| --config           | Path to the configuration file.                                      | config_base.ini or config_datahub.ini or any custom file |
| --print            | Selection of data to output.                                         | printenv, printmeta, printall                            |
| --format-json      | Enables pretty-printing for JSON console output.                     | Flag                                                     |
| --export-df-to-xls | Exports the metadata DataFrame to /home/cdsw/spark_app_summary.xlsx. | Flag                                                     |🔍 


## Output Modes
`printenv`: (Default) Focused on the runtime environment. Lists all sparkProperties for each application attempt.
`printmeta`: High-level summary. Aggregates metadata and resource profiles across all applications into a tabular format.
`printall`: Detailed audit. Includes JSON dumps of Job, Stage, and Executor details, as well as specific Task summaries.


## Example output

~~~
Spark App ID:  application_1752523212569_0121

Spark Attempt ID:  0
spark.app.attempt.id: 1
spark.app.id: application_1752523212569_0121
spark.app.name: PythonSQL
spark.app.startTime: 1752620910626
spark.app.submitTime: 1752620896893
spark.authenticate: false
spark.driver.extraJavaOptions: -Djava.net.preferIPv6Addresses=false -XX:+IgnoreUnrecognizedVMOptions --add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.lang.invoke=ALL-UNNAMED --add-opens=java.base/java.lang.reflect=ALL-UNNAMED --add-opens=java.base/java.io=ALL-UNNAMED --add-opens=java.base/java.net=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED --add-opens=java.base/java.util.concurrent=ALL-UNNAMED --add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED --add-opens=java.base/jdk.internal.ref=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.cs=ALL-UNNAMED --add-opens=java.base/sun.security.action=ALL-UNNAMED --add-opens=java.base/sun.util.calendar=ALL-UNNAMED --add-opens=java.security.jgss/sun.security.krb5=ALL-UNNAMED -Djdk.reflect.useDirectMethodHandle=false --add-exports=java.base/sun.net.dns=ALL-UNNAMED --add-exports=java.base/sun.net.util=ALL-UNNAMED
spark.driver.extraLibraryPath: /opt/cloudera/parcels/CDH-7.3.1-1.cdh7.3.1.p400.67986116/lib/hadoop/lib/native
spark.driver.host: spark-cluster-arm-worker1.pdf-jul2.a465-9q4k.cloudera.site
spark.driver.log.dfsDir: hdfs:///user/spark/driver3Logs
spark.driver.log.persistToDfs.enabled: true
spark.driver.port: 37739
spark.dynamicAllocation.enabled: true
spark.dynamicAllocation.executorIdleTimeout: 60
spark.dynamicAllocation.maxExecutors: 20
spark.dynamicAllocation.minExecutors: 1
spark.dynamicAllocation.schedulerBacklogTimeout: 1
spark.eventLog.dir: hdfs:///user/spark/spark3ApplicationHistory
spark.eventLog.enabled: true
spark.executor.cores: 4
spark.executor.extraJavaOptions: -Djava.net.preferIPv6Addresses=false -XX:+IgnoreUnrecognizedVMOptions --add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.lang.invoke=ALL-UNNAMED --add-opens=java.base/java.lang.reflect=ALL-UNNAMED --add-opens=java.base/java.io=ALL-UNNAMED --add-opens=java.base/java.net=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED --add-opens=java.base/java.util.concurrent=ALL-UNNAMED --add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED --add-opens=java.base/jdk.internal.ref=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.cs=ALL-UNNAMED --add-opens=java.base/sun.security.action=ALL-UNNAMED --add-opens=java.base/sun.util.calendar=ALL-UNNAMED --add-opens=java.security.jgss/sun.security.krb5=ALL-UNNAMED -Djdk.reflect.useDirectMethodHandle=false --add-exports=java.base/sun.net.dns=ALL-UNNAMED --add-exports=java.base/sun.net.util=ALL-UNNAMED
spark.executor.extraLibraryPath: /opt/cloudera/parcels/CDH-7.3.1-1.cdh7.3.1.p400.67986116/lib/hadoop/lib/native
spark.executor.id: driver
spark.executor.memory: 4g
spark.executorEnv.MKL_NUM_THREADS: 1
spark.executorEnv.OPENBLAS_NUM_THREADS: 1
spark.executorEnv.PYTHONPATH: /opt/cloudera/cm-agent/lib/python3.11/site-packages:/opt/cloudera/cm-agent/thirdparty<CPS>/opt/cloudera/parcels/CDH-7.3.1-1.cdh7.3.1.p400.67986116/lib/spark3/python/lib/py4j-0.10.9.7-src.zip<CPS>/opt/cloudera/parcels/CDH-7.3.1-1.cdh7.3.1.p400.67986116/lib/spark3/python/lib/pyspark.zip
spark.extraListeners: com.hortonworks.spark.atlas.SparkAtlasEventTracker
spark.hadoop.fs.s3a.committer.name: directory
spark.hadoop.fs.s3a.ssl.channel.mode: openssl
spark.hadoop.iceberg.engine.hive.enabled: true
spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version: 1
spark.iceberg.enabled: true
spark.io.encryption.enabled: false
spark.kerberos.access.hadoopFileSystems: s3a://pdf-jul25-buk-c00d5107
spark.lineage.enabled: true
spark.master: yarn
spark.network.crypto.enabled: false
spark.org.apache.hadoop.yarn.server.webproxy.amfilter.AmIpFilter.param.PROXY_HOSTS: spark-cluster-arm-master0.pdf-jul2.a465-9q4k.cloudera.site,spark-cluster-arm-master1.pdf-jul2.a465-9q4k.cloudera.site
spark.org.apache.hadoop.yarn.server.webproxy.amfilter.AmIpFilter.param.PROXY_URI_BASES: https://spark-cluster-arm-gateway.pdf-jul2.a465-9q4k.cloudera.site:443/spark-cluster-arm/cdp-proxy/yarn/proxy/application_1752523212569_0121,https:/spark-cluster-arm-master1.pdf-jul2.a465-9q4k.cloudera.site:8090/proxy/application_1752523212569_0121
spark.org.apache.hadoop.yarn.server.webproxy.amfilter.AmIpFilter.param.RM_HA_URLS: spark-cluster-arm-master0.pdf-jul2.a465-9q4k.cloudera.site:8090,spark-cluster-arm-master1.pdf-jul2.a465-9q4k.cloudera.site:8090
spark.rdd.compress: True
spark.scheduler.mode: FIFO
spark.serializer: org.apache.spark.serializer.KryoSerializer
spark.serializer.objectStreamReset: 100
spark.shuffle.service.enabled: true
spark.shuffle.service.port: 7447
spark.sql.catalog.local: org.apache.iceberg.spark.SparkCatalog
spark.sql.catalog.local.type: hadoop
spark.sql.catalog.spark_catalog: org.apache.iceberg.spark.SparkSessionCatalog
spark.sql.catalog.spark_catalog.type: hive
spark.sql.extensions: org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions
spark.sql.parquet.output.committer.class: org.apache.spark.internal.io.cloud.BindingParquetOutputCommitter
spark.sql.queryExecutionListeners: com.hortonworks.spark.atlas.SparkAtlasEventTracker
spark.sql.sources.commitProtocolClass: org.apache.spark.internal.io.cloud.PathOutputCommitProtocol
spark.sql.streaming.streamingQueryListeners: com.hortonworks.spark.atlas.SparkAtlasStreamingQueryEventTracker
spark.submit.deployMode: cluster
spark.submit.pyFiles:
spark.ui.enabled: true
spark.ui.filters: org.apache.hadoop.yarn.server.webproxy.amfilter.AmIpFilter
spark.ui.killEnabled: true
spark.ui.port: 0
spark.yarn.am.extraLibraryPath: /opt/cloudera/parcels/CDH-7.3.1-1.cdh7.3.1.p400.67986116/lib/hadoop/lib/native
spark.yarn.app.container.log.dir: /hadoopfs/ephfs1/nodemanager/log/application_1752523212569_0121/container_1752523212569_0121_01_000001
spark.yarn.app.id: application_1752523212569_0121
spark.yarn.appMasterEnv.MKL_NUM_THREADS: 1
spark.yarn.appMasterEnv.OPENBLAS_NUM_THREADS: 1
spark.yarn.config.gatewayPath: /opt/cloudera/parcels
spark.yarn.config.replacementPath: {{HADOOP_COMMON_HOME}}/../../..
spark.yarn.historyServer.address: http://spark-cluster-arm-master1.pdf-jul2.a465-9q4k.cloudera.site:18089
spark.yarn.historyServer.allowTracking: true
spark.yarn.isPython: true
spark.yarn.jars: local:/opt/cloudera/parcels/CDH-7.3.1-1.cdh7.3.1.p400.67986116/lib/spark3/jars/*,local:/opt/cloudera/parcels/CDH-7.3.1-1.cdh7.3.1.p400.67986116/lib/spark3/hive/*
spark.yarn.submit.waitAppCompletion: false
spark.yarn.tags: livy-batch-1-cllamf0z

Spark App ID:  application_1752523212569_0100

Spark Attempt ID:  0
spark.app.attempt.id: 1
spark.app.id: application_1752523212569_0100
spark.app.name: PythonSQL
spark.app.startTime: 1752604168178
spark.app.submitTime: 1752604158447
spark.authenticate: false
spark.driver.extraJavaOptions: -Djava.net.preferIPv6Addresses=false -XX:+IgnoreUnrecognizedVMOptions --add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.lang.invoke=ALL-UNNAMED --add-opens=java.base/java.lang.reflect=ALL-UNNAMED --add-opens=java.base/java.io=ALL-UNNAMED --add-opens=java.base/java.net=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED --add-opens=java.base/java.util.concurrent=ALL-UNNAMED --add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED --add-opens=java.base/jdk.internal.ref=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.cs=ALL-UNNAMED --add-opens=java.base/sun.security.action=ALL-UNNAMED --add-opens=java.base/sun.util.calendar=ALL-UNNAMED --add-opens=java.security.jgss/sun.security.krb5=ALL-UNNAMED -Djdk.reflect.useDirectMethodHandle=false --add-exports=java.base/sun.net.dns=ALL-UNNAMED --add-exports=java.base/sun.net.util=ALL-UNNAMED
spark.driver.extraLibraryPath: /opt/cloudera/parcels/CDH-7.3.1-1.cdh7.3.1.p400.67986116/lib/hadoop/lib/native
spark.driver.host: spark-cluster-arm-worker2.pdf-jul2.a465-9q4k.cloudera.site
spark.driver.log.dfsDir: hdfs:///user/spark/driver3Logs
spark.driver.log.persistToDfs.enabled: true
spark.driver.port: 35949
spark.dynamicAllocation.enabled: true
spark.dynamicAllocation.executorIdleTimeout: 60
spark.dynamicAllocation.maxExecutors: 20
spark.dynamicAllocation.minExecutors: 1
spark.dynamicAllocation.schedulerBacklogTimeout: 1
spark.eventLog.dir: hdfs:///user/spark/spark3ApplicationHistory
spark.eventLog.enabled: true
spark.executor.cores: 4
spark.executor.extraJavaOptions: -Djava.net.preferIPv6Addresses=false -XX:+IgnoreUnrecognizedVMOptions --add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.lang.invoke=ALL-UNNAMED --add-opens=java.base/java.lang.reflect=ALL-UNNAMED --add-opens=java.base/java.io=ALL-UNNAMED --add-opens=java.base/java.net=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED --add-opens=java.base/java.util.concurrent=ALL-UNNAMED --add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED --add-opens=java.base/jdk.internal.ref=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.cs=ALL-UNNAMED --add-opens=java.base/sun.security.action=ALL-UNNAMED --add-opens=java.base/sun.util.calendar=ALL-UNNAMED --add-opens=java.security.jgss/sun.security.krb5=ALL-UNNAMED -Djdk.reflect.useDirectMethodHandle=false --add-exports=java.base/sun.net.dns=ALL-UNNAMED --add-exports=java.base/sun.net.util=ALL-UNNAMED
spark.executor.extraLibraryPath: /opt/cloudera/parcels/CDH-7.3.1-1.cdh7.3.1.p400.67986116/lib/hadoop/lib/native
spark.executor.id: driver
spark.executor.memory: 4g
spark.executorEnv.MKL_NUM_THREADS: 1
spark.executorEnv.OPENBLAS_NUM_THREADS: 1
spark.executorEnv.PYTHONPATH: /opt/cloudera/cm-agent/lib/python3.11/site-packages:/opt/cloudera/cm-agent/thirdparty<CPS>/opt/cloudera/parcels/CDH-7.3.1-1.cdh7.3.1.p400.67986116/lib/spark3/python/lib/py4j-0.10.9.7-src.zip<CPS>/opt/cloudera/parcels/CDH-7.3.1-1.cdh7.3.1.p400.67986116/lib/spark3/python/lib/pyspark.zip
spark.extraListeners: com.hortonworks.spark.atlas.SparkAtlasEventTracker
spark.hadoop.fs.s3a.committer.name: directory
spark.hadoop.fs.s3a.ssl.channel.mode: openssl
spark.hadoop.iceberg.engine.hive.enabled: true
spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version: 1
spark.iceberg.enabled: true
spark.io.encryption.enabled: false
spark.kerberos.access.hadoopFileSystems: s3a://pdf-jul25-buk-c00d5107
spark.lineage.enabled: true
spark.master: yarn
spark.network.crypto.enabled: false
spark.org.apache.hadoop.yarn.server.webproxy.amfilter.AmIpFilter.param.PROXY_HOSTS: spark-cluster-arm-master0.pdf-jul2.a465-9q4k.cloudera.site,spark-cluster-arm-master1.pdf-jul2.a465-9q4k.cloudera.site
spark.org.apache.hadoop.yarn.server.webproxy.amfilter.AmIpFilter.param.PROXY_URI_BASES: https://spark-cluster-arm-gateway.pdf-jul2.a465-9q4k.cloudera.site:443/spark-cluster-arm/cdp-proxy/yarn/proxy/application_1752523212569_0100,https:/spark-cluster-arm-master1.pdf-jul2.a465-9q4k.cloudera.site:8090/proxy/application_1752523212569_0100
spark.org.apache.hadoop.yarn.server.webproxy.amfilter.AmIpFilter.param.RM_HA_URLS: spark-cluster-arm-master0.pdf-jul2.a465-9q4k.cloudera.site:8090,spark-cluster-arm-master1.pdf-jul2.a465-9q4k.cloudera.site:8090
spark.rdd.compress: True
spark.scheduler.mode: FIFO
spark.serializer: org.apache.spark.serializer.KryoSerializer
spark.serializer.objectStreamReset: 100
spark.shuffle.service.enabled: true
spark.shuffle.service.port: 7447
spark.sql.catalog.local: org.apache.iceberg.spark.SparkCatalog
spark.sql.catalog.local.type: hadoop
spark.sql.catalog.spark_catalog: org.apache.iceberg.spark.SparkSessionCatalog
spark.sql.catalog.spark_catalog.type: hive
spark.sql.extensions: org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions
spark.sql.parquet.output.committer.class: org.apache.spark.internal.io.cloud.BindingParquetOutputCommitter
spark.sql.queryExecutionListeners: com.hortonworks.spark.atlas.SparkAtlasEventTracker
spark.sql.sources.commitProtocolClass: org.apache.spark.internal.io.cloud.PathOutputCommitProtocol
spark.sql.streaming.streamingQueryListeners: com.hortonworks.spark.atlas.SparkAtlasStreamingQueryEventTracker
spark.submit.deployMode: cluster
spark.submit.pyFiles:
spark.ui.enabled: true
spark.ui.filters: org.apache.hadoop.yarn.server.webproxy.amfilter.AmIpFilter
spark.ui.killEnabled: true
spark.ui.port: 0
spark.yarn.am.extraLibraryPath: /opt/cloudera/parcels/CDH-7.3.1-1.cdh7.3.1.p400.67986116/lib/hadoop/lib/native
spark.yarn.app.container.log.dir: /hadoopfs/ephfs1/nodemanager/log/application_1752523212569_0100/container_1752523212569_0100_01_000001
spark.yarn.app.id: application_1752523212569_0100
spark.yarn.appMasterEnv.MKL_NUM_THREADS: 1
spark.yarn.appMasterEnv.OPENBLAS_NUM_THREADS: 1
spark.yarn.config.gatewayPath: /opt/cloudera/parcels
spark.yarn.config.replacementPath: {{HADOOP_COMMON_HOME}}/../../..
spark.yarn.historyServer.address: http://spark-cluster-arm-master1.pdf-jul2.a465-9q4k.cloudera.site:18089
spark.yarn.historyServer.allowTracking: true
spark.yarn.isPython: true
spark.yarn.jars: local:/opt/cloudera/parcels/CDH-7.3.1-1.cdh7.3.1.p400.67986116/lib/spark3/jars/*,local:/opt/cloudera/parcels/CDH-7.3.1-1.cdh7.3.1.p400.67986116/lib/spark3/hive/*
spark.yarn.submit.waitAppCompletion: false
spark.yarn.tags: livy-batch-0-rpr4xnyk
~~~