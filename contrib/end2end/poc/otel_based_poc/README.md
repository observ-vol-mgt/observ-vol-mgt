# PoC usecase
![demofigure](../../../../docs/images/poc_otel.svg)

The PoC demonstrates two edges connected to a central cloud. 
Each edge comprises metric generator whose metrics are scraped by an oTel collector. 
The collector does a remote write to thanos (running in the central cloud) for long term storage and analysis. 
The remote write is intercepted as part of the oTel processor pipeline workflow. 
A "configuration proxy" is used to apply various transformations from the central cloud 
to the processors inside the oTel collectors. 

In this PoC we showcase how our controller generate insights that trigger pruning of metrics based on similarity across east and west edge/clouds.

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
There should be a single metric for each edge, hence a total of four metrics.
3. Next, we trigger the controller to draw insights
```commandline
make perform_analysis
```
or
Via the manager API. `http://127.0.0.1:5010/apidocs/#/Controller/post_api_v1_analyze`
4. Verify the generated insights in the Controller UI: `http://127.0.0.1:5000/insights`  
Click `Insights details 4` and the analysis should show three metrics
(`k8s_pod_network_bytes($app,c0,metricgen2:8001,west,$IP),nwdaf_5G_network_utilization(analytic_function,c0,metricgen1:8000,east,$IP),nwdaf_5G_network_utilization(analytic_function,c0,metricgen2:8001,west,$IP) `)
that are correlated with `k8s_pod_network_bytes`.
5. The insights can be used just as a recommendation or for full-automation where corresponding transform will be applied to each edge to handle the pruning. In this poc we will run in full automation mode. 
6. The controller triggers transformation in each cloud which can be seen using the manager UI   
Access `http://127.0.0.1:5010/apidocs/#/Processor%20Configuration/getProcessorConfig`.  
Use `east` and `west` in the UI combo box as the processor ids to check transformation added to individual clouds. 
7. You can visualize the change in the metrics values 
Execute the query `k8s_pod_network_bytes or nwdaf_5G_network_utilization`) in the `thanos query` UI (in graph mode). 
You will see only `k8s_pod_network_bytes` with label ` processor="east"` flowing.
Other analyzed as similar metrics are now being pruned/dropped.
8. To end the POC and clean docker execute  
```commandline
make end
```
or 
```commandline
docker compose -f docker-compose-otel.yml down
```
