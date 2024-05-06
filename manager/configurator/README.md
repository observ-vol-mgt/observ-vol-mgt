# Processor Management API

## Overview
This Flask application serves as an API for managing edge processors. It provides endpoints to create, retrieve, and delete individual processors, as well as to perform these operations in bulk.

## Getting Started
To run the application, ensure you have Python installed. Install Flask and other dependencies by running:

```bash
pip install -r requirements.txt
```

## Configuration

The application requires a configuration file named config.py containing the URLs of edge processors. Ensure that each processor URL follows the format PROCESSOR_<ID>_URL.


## API Endpoints

    GET /processors/<processor_id>: Retrieve details of a specific processor.
    GET /processors: Retrieve details of all processors.
    POST /processors/<processor_id>: Create a new processor or update an existing one.
    POST /processors: Create or update multiple processors.
    DELETE /processors/<processor_id>: Delete a specific processor.
    DELETE /processors: Delete all processors.


## Running the Application

Execute the following command:

``` bash
python main.py
```

The application will run on the host and port specified in the config.py. It will also save the logs and errors to a file specified in the config.py file.
