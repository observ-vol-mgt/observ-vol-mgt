
Flask App port = 5000

Prometheus Client Port = 8000

Sample CURL statements:

1. Set some metrics 

    >curl --location --request POST 'localhost:5000' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "type": "SET",
        "cluster": [
        {
        "name": "1",
        "clustermetrics": ["1","2","3"],
        "node": [
            {
            "name": "1",
            "nodemetrics": ["2","3"]
            },
            {
            "name": "2",
            "nodemetrics": ["2","7"]
            }
        ],
        "app": [
            {
            "name": "A",
            "appmetrics": ["3","4","5"]
            },
            {
            "name": "B",
            "appmetrics": ["1","2"]
            }
        ]
        }
        ]
    }'

2. Reset the same metrics 

    >curl --location --request POST 'localhost:5000' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "type": "RESET",
        "cluster": [
        {
        "name": "1",
        "clustermetrics": ["1","2","3"],
        "node": [
            {
            "name": "1",
            "nodemetrics": ["2","3"]
            },
            {
            "name": "2",
            "nodemetrics": ["2","7"]
            }
        ],
        "app": [
            {
            "name": "A",
            "appmetrics": ["3","4","5"]
            },
            {
            "name": "B",
            "appmetrics": ["1","2"]
            }
        ]
        }
        ]
    }'

3. Set all metrics

    >curl --location --request POST 'localhost:5000' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "type": "SET ALL"
    }'

4. Reset all metrics

    >curl --location --request POST 'localhost:5000' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "type": "RESET ALL"
    }'