# PoC use-case
![demofigure](../../../../docs/images/poc_otel.svg)

The PoC demonstrates two edges connected to a central cloud. 
Each edge comprises a metric generator whose metrics are scraped by an OTel collector. 
The collector does a remote write to Thanos (running in the central cloud) for long-term storage and analysis. 
The remote write is intercepted as part of the OTel processor pipeline workflow. 
A "configuration proxy" is used to apply various transformations from the central cloud 
to the processors inside the OTel collectors. 

This PoC uses a customized OTel collector and showcases how the controller generates insights that trigger adjusting frequency of metrics collection for monotone metrics on the east and west edges/clouds.

## Environment Setup

The PoC requires docker installed on the machine to test the scenario. 
The following containers get installed when the PoC environment is bought up.

Central containers:
- `thanos-receive`
- `thanos-query`
- `thanos-ruler`
- `ruler-config`
- `alertmanager`
- `controller`
- `manager`

Edge containers:
- `metricgen_[east,west]`
- `otel_proxy_collector_[east,west]`
- `otel_collector_[east,west]`

## Running the PoC story

1. Bring up the PoC environment
```commandline
make start
```
or 
```commandline
docker-compose -f docker-compose-otel.yml up -d
```
2. Confirm that the metrics are flowing correctly in the `thanos query` UI: `http://127.0.0.1:19192`  
Confirm metrics `k8s_pod_network_bytes` or `nwdaf_5G_network_utilization` are available.  
Confirm metrics `process_cpu_seconds_total` are available and are collected at 5 second intervals.
Let the demo run until the `k8s_pod_network_bytes` metric is no longer monotone.
3. Next, we trigger the controller to draw insights
```commandline
make perform_analysis
```
or
Via the manager API. `http://127.0.0.1:5010/apidocs/#/Controller/post_api_v1_analyze`
4. Verify the generated insights in the Controller UI: `http://127.0.0.1:5000/insights`  
Click `Insights details 3` and the analysis should show the list of metrics identified as monotone.
This should include the metric `process_cpu_seconds_total`.
5. The insights can be used just as a recommendation or for full automation, where a corresponding transform will be applied to each edge to handle the pruning. In this post, we will run in full automation mode. 
6. The controller triggers transformation in each cloud which can be seen using the manager UI   
Access `http://127.0.0.1:5010/apidocs/#/Processor%20Configuration/getProcessorConfig`.  
Use `east` and `west` in the UI combo box as the processor ids to check the transformation added to individual clouds. 
7. You can visualize the change in the metrics values 
Execute the query `process_cpu_seconds_total` in the `thanos query` UI (in graph mode). 
You will see that the frequency of the update of the metric has changed from 5 seconds to 30 seconds.
Execute the query `k8s_pod_network_bytes` in the `thanos query` UI (in graph mode). 
You will see that the frequency of the update of the metric remains unchanged at 5 seconds.
8. To end the POC and clean docker execute  
```commandline
make end
```
or 
```commandline
docker compose -f docker-compose-otel.yml down
```
