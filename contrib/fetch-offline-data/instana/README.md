# Instana Metrics and Events Fetcher

This Python script allows you to fetch metrics and events data from Instana using its REST API and save the data to JSON files.

## Motivation

Instana is a popular monitoring tool used by many organizations to monitor their infrastructure and applications. This script provides a convenient way to programmatically fetch metrics and events data from Instana, allowing users to analyze and process the data as needed.

## Usage

1. **Installation**: Before running the script, make sure you have Python installed on your system. You can download and install Python from [python.org](https://www.python.org/).

2. **Dependencies**: Install the required Python packages using pip:

   ```bash
   pip install requests
   ```
   
3. **Configuration**: You need to obtain an Instana API token and know the base URL of your Instana instance. Set these values in the script or provide them as command-line arguments (see below).
4. **Run the Script**: Use the following command to run the script:
```bash
python instana_fetcher.py --url YOUR_INSTANA_URL --token YOUR_API_TOKEN --fetch-events --start START_TIME --end END_TIME --output_dir OUTPUT_DIR
```

> Replace YOUR_INSTANA_URL and YOUR_API_TOKEN with the base URL of your Instana instance and your API token, respectively.
   
> You can also specify the START_TIME and END_TIME in the format YYYY-MM-DDTHH:MM:SS to fetch data for a specific time window.  
> If you omit the --start and --end parameters, the script will fetch data for the last 24 hours by default.

> You can also specify the output_dir to save the data into a specific directory.  
> If you omit the --output_dir parameter, the script will save the data into the current directory.  

> By default, the script fetches metrics only, specify --fetch-events to include also events  


5. **Output**: The script will save the fetched metrics and events data to JSON files named instana_metrics.json and instana_events.json, respectively.
