# PoC usecase
![demofigure](../../../../docs/images/pocv1.svg)

The PoC demonstrates two edges connected to a central cloud. Each edge comprises of metric generator whose metrics are scraped by prometheus. The prometheus does a remote write to thanos (running in the central cloud) for long term storage and analysis. The remote write is intercepted by our processor proxy running at each edge location. The processor applies various transformation to the collected metrics.

In this PoC we showcase two transformations.
- On east cloud/edge we showcase the need to control the bandwidth utilization. We identify the increase in bandwidth utilization using alerts and our manager triggers addition of the filter transformation on processor running on east cloud/edge. This will limit the volume of data sent from east edge. 
- On west cloud/edge, we showcase the need to change the frequency of metric collection for a particular app/cluster. This scenario arises when for example an issue is identified at a node in a cluster and you need metrics for that node at a higher frequency to fix this issue. The identification of the issue in the PoC is also done with help of alerts on the metrics. 

Both the PoC scenarios which can also happen simulatenously, we also showcase how we revert the applied transformation once the issue is resolved. We instrument the issue with increase in metric values and reduce the value to revert the issue. 

## Environment Setup

### Docker

The PoC requires docker installed on the machine to test the scenario. The following containers get installed when the PoC environment is bought up.\
Central containers:
- `thanos-receive`
- `thanos-query`
- `thanos-ruler`
- `ruler-config`
- `alertmanager`
- `manager`\
Edge containers:
- `metricgen1,2`
- `prometheus1,2`
- `pmf_processsor1,2`

### Kubernetes

The PoC requires a kubernetes cluster to test the scenario. The following pods get deployed when the PoC environment is bought up.\
Central pods:
- `thanos` (comprising the thanos-receive and thanos-query containers)
- `thanos-ruler` (comprising the thanos-ruler and ruler-config containers)
- `alertmanager`
- `manager`\
Edge containers:
- `metricgen1,2`
- `prometheus1,2`
- `pmf_processsor1,2`

## Understanding the Rules specification

The rules are specified by the user in a yaml format. The manager parses them and applies them to the thanos ruler with the help of the `ruler_config` container. The rules file that the user specifies as part of the demo is `demo_2rules.yaml`. As per the file we apply two rules:
- First rule `rule_1` is applied for metrics received from east edge. The rule is triggered when the metric `app_A_network_metric_0{IP="192.168.1.3"}` cross the value of 200. The specification also mentions what needs to be done when the alert is triggered (`firing_action`). In the demo for this cloud, we add a new transform to filter all other metrics and allow just `app_A_network_metric_0` for IP 192.168.1.3 from cloud east. The `resolved_action` specifies what to be done when the alert is resolved. Here, we simply remove the added transform.
- Second rule `rule_2` is applied for metics received from west edge. The rule is triggered when the metric `cluster_hardware_metric_0{node="0"}` cross the value of 200. The `firing_action` is to increase the frequency of `cluster_hardware_metric_0` for `node:0` to 5 seconds.

Note that the actions (firing and resolved) are stored by the manager and applied to the corresponding edge processor when the alert is fired/resolved.

## Running the PoC story - Docker

1. Bring up the PoC environment
``` 
docker-compose -f docker-compose-quay.yml up -d
```
2. Add the rules and actions (in the form of transformation) corresponding to the rule
```
curl -X POST --data-binary @demo_2rules.yaml -H "Content-type: text/x-yaml" http://0.0.0.0:5010/api/v1/rules
```
3. Confirm the two rules are added correctly in the `thanos ruler` UI:
`http://0.0.0.0:10903/rules`
4. Confirm the metrics are flowing correctly in the `thanos query` UI:
`http://0.0.0.0:19192/`\
Search for `cluster_hardware_metric_0` and `app_A_network_metric_0`. You should see 6 metrics (3 for each edge) for each of these. The edge can be identified by the `processor` label in the metric.
5. Next, we instrument the issue scenario with metric value change. We apply the value change to metricgen for each edges (`metricgen1` and `metricgen2`)
    - For issue at east edge: `curl -X POST --data-binary @change_appmetric.yml -H "Content-type: text/x-yaml" http://0.0.0.0:5002`
    - For issue at west edge: `curl -X POST --data-binary @change_hwmetric.yml -H "Content-type: text/x-yaml" http://0.0.0.0:5003`
6. You can visualize the change in the metrics value in the `thanos query` UI (in the graph mode)
7. The alert should also be firing and can be seen in the `thanos ruler` UI (`http://0.0.0.0:10903/alerts`)
   P.S. Wait for 30sec-1min before checking this step. 
8. The manager triggers adding of the corresponding transforms. To check the transforms added got to Manager API: `http://0.0.0.0:5010/apidocs/#/Processor%20Configuration/getProcessorConfig` and use `east` and `west` as processor id.\
   P.S. This step is just for extra confirmation and is optional. 
9. To visualize the transformation thanos query UI (in the graph mode).
    - If you search `app_A_network_metric_0{processor="east"}` you will see the metric with label `IP:192.168.1.3` has changing value but the other metrics with label `IP:192.168.1.1` and `IP:192.168.1.2` with no change (straight line; showcasing no value change or should stop completely).\ This is because we have filtered and allowed `app_A_network_metric_0` only for app with `IP:192.168.1.3`.
    - If you search `cluster_hardware_metric_0{processor="west"}` you will see the metric with label `node:'0'` having a nice sinusoidal wave. This is because its value is changing every 5 sec. The other metrics with label `node:'1'` and `node:'2'` will be blocky showing their frequency is still 30 sec. 
This showcases the transformation happening in an automated fashion.
10. We will just revert issue in edge cloud east and showcase that we work on specific cloud as well.
    ```
    curl -X POST --data-binary @change_appmetricRESET.yml -H "Content-type: text/x-yaml" http://0.0.0.0:5002
    ```
    In sometime, you should see the alert rule 1 resolved (in thanos ruler UI (`http://0.0.0.0:10903/alerts`)) and should see the metric `app_A_network_metric_0{processor="east"}` again coming in for labels `IP:192.168.1.1` and `IP:192.168.1.2` as well demontrating the removal of `filter` transform from edge cloud 1. 

11. P.S. One can revert the transformation applied to west edge as well using the below command.
    ```
    curl -X POST --data-binary @change_hwmetricRESET.yml -H "Content-type: text/x-yaml" http://0.0.0.0:5003
    ```
-   Note: The PoC can also be tested with using OTel Collector instead of prometheus. For this the only step that will change is - <em> 1. Bring up the PoC environment</em> to below
    ``` 
    docker-compose -f docker-compose-otel.yml up -d
    ```

## Running the PoC story - Kubernetes

1. The `k8s` directory contains the specifications for deployments, services, PVCs and PVClaims for the POC. It also includes the ingress definitions. The ingress definitions require the `APP_HOST` variable to be set to the DNS address configured for applications running on your kubernetes cluster. The following make command will create an `ovm` namespace, sed the specified `APPHOST` variable into the ingress definitions and apply the resources to the cluster.
```
APPHOST=your-desired-apphost make up-k8s-kubectl
``` 
2. Add the rules and actions (in the form of transformation) corresponding to the rule
```
curl -X POST --data-binary @demo_2rules.yaml -H "Content-type: text/x-yaml" http://manager.YOUR_APP_HOST/api/v1/rules
```
3. Confirm the two rules are added correctly in the `thanos ruler` UI:
`http://thanos-ruler.YOUR_APP_HOST/rules`
4. Confirm the metrics are flowing correctly in the `thanos query` UI:
`http://thanos-query.YOUR_APP_HOST`\
Search for `cluster_hardware_metric_0` and `app_A_network_metric_0`. You should see 6 metrics (3 for each edge) for each of these. The edge can be identified by the `processor` label in the metric.
5. Next, we instrument the issue scenario with metric value change. We apply the value change to metricgen for each edges (`metricgen1` and `metricgen2`)
    - For issue at east edge: `curl -X POST --data-binary @change_appmetric.yml -H "Content-type: text/x-yaml" http://metricgen1.YOUR_APP_HOST`
    - For issue at west edge: `curl -X POST --data-binary @change_hwmetric.yml -H "Content-type: text/x-yaml" http://metricgen2.YOUR_APP_HOST`
6. You can visualize the change in the metrics value in the `thanos query` UI (in the graph mode)
7. The alert should also be firing and can be seen in the `thanos ruler` UI (`http://thanos-ruler.YOUR_APP_HOST/alerts`)
   P.S. Wait for 30sec-1min before checking this step. 
8. The manager triggers adding of the corresponding transforms. To check the transforms added got to Manager API: `http://manager.YOUR_APP_HOST/apidocs/#/Processor%20Configuration/getProcessorConfig` and use `east` and `west` as processor id.\
   P.S. This step is just for extra confirmation and is optional. 
9. To visualize the transformation thanos query UI (in the graph mode).
    - If you search `app_A_network_metric_0{processor="east"}` you will see the metric with label `IP:192.168.1.3` has changing value but the other metrics with label `IP:192.168.1.1` and `IP:192.168.1.2` with no change (straight line; showcasing no value change or should stop completely).\ This is because we have filtered and allowed `app_A_network_metric_0` only for app with `IP:192.168.1.3`.
    - If you search `cluster_hardware_metric_0{processor="west"}` you will see the metric with label `node:'0'` having a nice sinusoidal wave. This is because its value is changing every 5 sec. The other metrics with label `node:'1'` and `node:'2'` will be blocky showing their frequency is still 30 sec. 
This showcases the transformation happening in an automated fashion.
10. We will just revert issue in edge cloud east and showcase that we work on specific cloud as well.
    ```
    curl -X POST --data-binary @change_appmetricRESET.yml -H "Content-type: text/x-yaml" http://metricgen1.YOUR_APP_HOST
    ```
    In sometime, you should see the alert rule 1 resolved (in thanos ruler UI (`http://thanos-ruler.YOUR_APP_HOST/alerts`)) and should see the metric `app_A_network_metric_0{processor="east"}` again coming in for labels `IP:192.168.1.1` and `IP:192.168.1.2` as well demontrating the removal of `filter` transform from edge cloud 1. 

11. P.S. One can revert the transformation applied to west edge as well using the below command.
    ```
    curl -X POST --data-binary @change_hwmetricRESET.yml -H "Content-type: text/x-yaml" http://metricgen2.YOUR_APP_HOST

    ```

