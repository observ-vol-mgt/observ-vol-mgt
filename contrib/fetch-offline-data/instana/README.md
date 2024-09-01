# Instana Observability Data Fetchers


> GitHub reference: [fetch-offline-data/instana](https://github.com/observ-vol-mgt/observ-vol-mgt/tree/main/contrib/fetch-offline-data/instana) 

Those Python scripts allow fetching metrics, events, traces and topology data from Instana using REST API.
The scripts persist the data in JSON format into files.

## Motivation

Instana is a popular monitoring tool used by many organizations to monitor their infrastructure and applications. This script provides a convenient way to programmatically fetch metrics and events data from Instana, allowing users to analyze and process the data as needed.

## Usage

1. **Installation**: Before running the scripts, make sure you have Python installed on your system. You can download and install Python from [python.org](https://www.python.org/).

2. **Dependencies**: Install the required Python packages using pip:

   ```bash
   pip install requests
   ```
   
3. **Configuration**: You need to obtain an Instana API token and know the base URL of your Instana instance. Set these values in the script or provide them as command-line arguments (see below).
4. **Execute the Scripts**: Use the following commands to run the relevant scripts:

# INSTANA Infrastructure metrics
## Args
1. `--log-level` - ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
2. `--start` - start date in YYYY-MM-DDTHH:MM:SS format
3. `--end` - end date in YYYY-MM-DDTHH:MM:SS format
4. `--url` - Instana instance bse url
5. `--token` - List of tokens (tokens will be rotated in api calls to prevent api limit error)
6. `--output_dir` - Folder to store retrieved data
7. `--plugin` - Filter data by plugin. Eg: prometheus
8. `--query` - Filter data by query. Eg: namespace=kube

## Example
* Fetching past 1 day data:
```bash
python fetch_instana_data.py --url https://wmlpreprod-ibmdataaiap.instana.io --token EN6NUPBATJit5SJI_**** --query namespace=watsonx-huggingface --plugin prometheus --start 2024-05-28T00:00:00 --end 2024-05-29T00:00:00 --output_dir data
```
* Fetching past 20 minutes:
```bash
python fetch_instana_data.py --url https://wmlpreprod-ibmdataaiap.instana.io --token EN6NUPBATJit5SJI_**** --query namespace=watsonx-huggingface --plugin prometheus --start 2024-05-28T23:40:00 --end 2024-05-29T00:00:00 --output_dir data
```
* Using default start time and end time with multiple tokens:
```bash
python fetch-instana-data.py --url https://wmlpreprod-ibmdataaiap.instana.io --token EN6NUPBATJit5SJI_**** JSY9IUWvQEapPBZ4yC**** --output_dir data
```

# INSTANA Application metrics
## Args
1. `--log-level` - ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
2. `--start` - start date in YYYY-MM-DDTHH:MM:SS format
3. `--end` - end date in YYYY-MM-DDTHH:MM:SS format
4. `--url` - Instana instance bse url
5. `--token` - List of tokens (tokens will be rotated in api calls to prevent api limit error)
6. `--output_dir` - Folder to store retrieved data

## Example
* Getting application metrics:
```bash
python fetch_instana_app_metrics.py --url https://instana1.tivlab.raleigh.ibm.com --token tmdOVgSMS7ucB2r**** y7l5tD1wR9G581LY**** tMd8pw4WS6SdLkx**  --start 2024-07-02T00:00:00 --end 2024-07-03T00:00:00 --output_dir data
```

# INSTANA Application topology
## Args
1. `--log-level` - ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
2. `--start` - start date in YYYY-MM-DDTHH:MM:SS format
3. `--end` - end date in YYYY-MM-DDTHH:MM:SS format
4. `--url` - Instana instance bse url
5. `--token` - Instana api token (string)
6. `--output_dir` - Folder to store retrieved data

## Example
* Getting application topology:
```bash
python fetch_instana_traces.py --traces_limit 10 --service_name_filter aggregator --url https://blue-instanaops.instana.io --token $apiToken --output_dir demo-eu
```

# INSTANA traces
## Args
1. `--log-level` - ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
2. `--start` - start date in YYYY-MM-DDTHH:MM:SS format
3. `--end` - end date in YYYY-MM-DDTHH:MM:SS format
4. `--url` - Instana instance bse url
5. `--token` - Instana api token (string)
6. `--service_name_filter` - Service name filter for traces
7. `--traces_limit` - Maximum number of traces to dump
8. `--output_dir` - Folder to store retrieved data

## Example
* Getting traces, limiting to 10 traces:
```bash
python fetch_instana_traces.py --url https://instana1.tivlab.raleigh.ibm.com --token y7l5tD1wR9G581LYO**** --traces_limit 10 --output_dir data
```

> [!NOTE]  
> Replace YOUR_INSTANA_URL and YOUR_API_TOKEN with the base URL of your Instana instance and your API token, respectively.
 
> You can also specify the START_TIME and END_TIME in the format YYYY-MM-DDTHH:MM:SS to fetch data for a specific time window.  
> If you omit the --start and --end parameters, the script will fetch data for the last 24 hours by default.

> You can also specify a QUERY string to limit fetching to subset of the instana snapshots  
> If you omit the --query parameters, the script will fetch data from all snapshots.

> You can also specify a PLUGINS_FILTER string to limit fetching to regex instana plugins  
> If you omit the --plugins_filter parameters, the script will fetch data from all plugins.
 
> You can also specify the OUTPUT_DIR to save the data into a specific directory.  
> If you omit the --output_dir parameter, the script will save the data into the current directory.  
 
> You can also specify the LIMIT to limit data fetching.  
> If you omit the --limit parameter, the script will limit to 1000 metrics.
 
> By default, the script fetches metrics only, specify --fetch-events to include also events (Not implemented yet)  

5. **Output**: The script will save the fetched metrics and events data to JSON files named instana_metrics.json and instana_events.json, respectively.

> [!NOTE]  
> It is possible to execute the script `convert-dump-metrics-file-to-promql-format.py` 
> as a post-processing stage, and convert output metrics files into
> promQL format dump file. This file can be used with the 
> as input to the volume manager controller.  
> 
> The default input file for the script is `instana_metrics.json` and the default
> output file is `promql_metrics.json`  
> 
> To load into the controller, execute from the controller directory:

```bash
python main.py --ingest_type=file --ingest_file=../contrib/fetch-offline-data/instana/promql_metrics.json --feature_extraction_type=tsfel --config_generator_type=otel --config_generator_directory=/tmp
```

> [!NOTE]  
> It is possible to execute the script `parse-instana-traces-queries-into-access-log.py`
> as a ost-processing stage, and convert output traces files into
> access_log format as input to the volume manager controller.
> 
> Example usage:
```bash
python parse-instana-traces-queries-into-access-log.py --input_file demo-eu/traces.json --output_dir demo-eu
```
