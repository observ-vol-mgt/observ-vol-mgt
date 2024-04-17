# End-To-End tests

This directory holds scripts and configuration for end-to-end tests of the observability volume controller.
The end-to-end tests are based upon local set-ups of two use cases:

1. prometheus at the edges and thanos at the hub 
2. oTel collector at the edges and prometheus at the hub

## Use case (1): prometheus at the edges and thanos at the hub   
To manually start e2e containers, use  `make up-prom-thanos`  
To shut down the containers, use: `make down-prom-thanos`

The setup automatically starts the following containers:  

### What does it start?

| Service               |                                                                              | Ports |
|-----------------------|------------------------------------------------------------------------------|-------|
| prometheus_one        | The first Prometheus server                                                  | 9001  |
| prometheus_two        | The second Prometheus server                                                 | 9002  |
| minio                 | A minio instance serving as Object Storage for store, compactor and sidecars | 9000  |
| minio-console         | user: myaccesskey password: mysecretkey                                      | 9007  |
| thanos_sidecar_one    | First Thanos sidecar for prometheus_one                                      |       |
| thanos_sidecar_two    | Second Thanos sidecar for prometheus_two                                     |       |
| thanos_querier        | Thanos querier instance connected to both sidecars and Thanos store          | 10902 |
| thanos_query_frontend | Thanos query frontend connected to querier                                   | 19090 |
| thanos_store          | A Thanos store instance connected to minio                                   | 10912 |

### query examples

For example, to get the  `go_memstats_frees_total` metric values 
from time stamp `1711895548` to timestamp `171189954` in steps of `560s` execute the query:

```bash
curl 'http://localhost:19090/api/v1/query_range?query=go_memstats_frees_total&start=1711895548&end=1711899548&step=560s' | jq
```

## Use case (2): oTel collector at the edges and prometheus at the hub   
To manually start e2e containers, use  `make up-otel-prom`  
To shut down the containers, use: `make down-otel-prom`

The setup automatically starts the following containers:  

### What does it start?

| Service            |                                   | Ports |
|--------------------|-----------------------------------|-------|
| prometheus_hub     | A Prometheus instance             | 9001  |
| otel_collector_one | The first otel collector instance | 18888 |
| otel_collector_two | The second collector instance     | 18889 |

### query examples

For example, to get the  `go_memstats_frees_total` metric values 
from time stamp `1711895548` to timestamp `171189954` in steps of `560s` execute the query:

```bash
curl 'http://localhost:9001/api/v1/query_range?query=system_cpu_time_seconds_total&start=1711895548&end=1711899548&step=560s' | jq
```
