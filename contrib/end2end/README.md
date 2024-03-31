# End-To-End tests

This directory holds scripts and configuration for end-to-end tests of the observability volume controller.
The end-to-end tests are based upon local set-up of prometheus and thanos along with deployments of the controller.

To manually start e2e containers, use  `make up`
To shut down the containers, use: `make down`

The setup automatically starts  the following containers:  

## What does it start?

| Service               |                                                                              | Ports |
|-----------------------|------------------------------------------------------------------------------|-------|
| prometheus_one        | The first Prometheus server                                                  | 9001  |
| prometheus_two        | The second Prometheus server                                                 | 9002  |
| minio                 | A minio instance serving as Object Storage for store, compactor and sidecars | 9000  |
| minio-console         |                                                                              | 9007  |
| thanos_sidecar_one    | First Thanos sidecar for prometheus_one                                      |       |
| thanos_sidecar_two    | Second Thanos sidecar for prometheus_two                                     |       |
| thanos_querier        | Thanos querier instance connected to both sidecars and Thanos store          | 10902 |
| thanos_query_frontend | Thanos query frontend connected to querier                                   | 19090 |
| thanos_store          | A Thanos store instance connected to minio                                   | 10912 |


