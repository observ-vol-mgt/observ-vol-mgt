<h1 align="center" style="border-bottom: none">
  <a href="https://prometheus.io" target="_blank"><img alt="OVM" src="/docs/images/OVM.png" width="120"></a><br>OVM
</h1>

[![push - build test and push](https://github.com/observ-vol-mgt/observ-vol-mgt/actions/workflows/push.yml/badge.svg)](https://github.com/observ-vol-mgt/observ-vol-mgt/actions/workflows/push.yml)
[![Open Issues](https://img.shields.io/github/issues-raw/observ-vol-mgt/observ-vol-mgt)](https://github.com/observ-vol-mgt/observ-vol-mgt/issues)
[![Docs](https://img.shields.io/badge/docs-latest-blue)](https://observ-vol-mgt.github.io/observ-vol-mgt/)

# OVM: Observability Volume Manager
In today's dynamic computing landscape spanning centralized clouds, multi-cloud, and edge computing, the demand for adaptable observability is paramount. In particular, managing the escalating volume of observability data is crucial. **Observability Volume Manager** addresses the complexities of dynamic observability data management by offering tailored processing capabilities to ensure efficient and effective observability across the entire computing infrastructure. 

## Overview
Observability Volume Manager provides a mechanism to perform various transformations on observability data to manage the volume and support various edge deployment use cases.  
- **OVM** minimizes compute, transport, and data persistency costs, while preserving the complete value of observability to detect, troubleshoot, and support analytics.
- **OVM** dynamically responds to changes in system state and behavior, optimizing observability volume based on user-defined policies.
- **OVM** encapsulates multiple layers of "smartness" and can be used in full automation mode or as a recommendation system supporting a "user in the loop" design.  
- **OVM** provides user-centric intent-based semantic language supporting multiple transformations represented as a DAG. This semantic language is deployment and technology-agnostic.

The current version of *OVM* supports
<img src="https://opentelemetry.io/img/logos/opentelemetry-logo-nav.png" alt="OpenTelemetry Icon" width="20" height=""> [OpenTelemetry](https://opentelemetry.io/docs/collector/) 
and 
<img src="https://github.com/prometheus/prometheus/raw/main/documentation/images/prometheus-logo.svg" alt="Prometheus Icon" width="20" height=""> [Prometheus](https://prometheus.io/) as observability data collectors.  

It uses either an **embedded**, lightweight, automated, SQL-based metric processing system  or the capabilities of the **community** [OTel processors](https://github.com/open-telemetry/opentelemetry-collector/blob/main/processor/README.md) to manage and change the collected observability volume.      

### Architecture: A Bird's Eye View

![](docs/images/architecture.svg)

The diagram above illustrates the system architecture of **Observability Volume Manager**. The system components i.e Processor, Manager, and Controller are deployed across the central cloud and edge locations:

**Central Cloud location**
  - The central cluster that is used to manage the edge clusters.
  - Can be an on-premise or cloud-based cluster.
  - There are no resources or network constraints expected in the core cluster.
  - There is an observability data aggregator (such as Prometheus, Thanos, Loki, etc.) running on the central cluster.
    
**Single Cloud/Edge location**
  - This is an edge environment where the user workloads are running.
  - The edge environment is expected to have moderate yet constrained compute resources and network.
  - There are observability data collectors (such as OTel, Prometheus, Vector, etc.) running on the edge environment that are sending the data to the aggregator in the central cluster. 


**Processor:** Is deployed at the edge location. It intercepts the observability data collected by the collectors before being pushed to the aggregators in the central cloud.
The Processor facilitates diverse transformations like filtering, aggregation, and granularity adjustments on the observability data. 
Users can also apply combinations of these transformations, represented as a Directed Acyclic Graph (DAG). 
More details on the processor can also be found in our [paper](docs/paper.pdf).

**otel-collector-proxy** is a new addition to OVM. 
It is deployed at the edge location and acts as an intermediary layer between OVM and OTel Collector.
It is responsible for translations and dynamically managing OTel collector processor configurations.

**Manager:** is deployed at the central cloud location and is responsible for managing observability data transformations at the edge locations. It is a user-facing component with a REST interface to create/update/delete the rules that define the transformation DAGs to be enabled on a certain edge site(s) when some condition is met. The user can also specify default transformation DAGs for edge sites. The Manager coordinates with the processors to enforce transformation DAGs based on user-defined rules when conditions are satisfied. 

**Controller:** is deployed at the central cloud location. 
It periodically analyzes the behavior of observability signals and correlates them with customer requirements and the usage of signals in the system. Utilizing this analysis, the Controller generates recommendations and can even automatically update rules in the manager to effectively manage and reduce observability data volume. 


> Note: When *OVM* uses OTel processor capabilities in the *otel-collector-proxy*, the functionality is 
> limited to the supported transformations available by OTel, additional details can be 
> found on [otel-collector-proxy/README.md](https://github.com/observ-vol-mgt/observ-vol-mgt/tree/main/otel-collector-proxy) and 
> on the [OTel processors page](https://github.com/open-telemetry/opentelemetry-collector/blob/main/processor/README.md)

### Use Cases
The main objective of the current version of **Observability Volume Manager** is to demonstrate centralized control and management of observability data across all connected edge environments from the core. Users can specify transformation DAGs for individual edge locations through rules, which define conditions based on metrics collected from these environments. 

> The **contrib** folder holds various tools and scripts that helps to develop, build, and maintain the project. It also contains the docker compose to bring up all the components needed to run the proof of concept scenario locally.

## Getting started 

To demonstrate the value of *OVM* and provide a "learning by example" getting started experience, OVM provides several **Proof of Concept**s experiences.
Each POC includes **documentation and deployment** of OVM and additional components demonstrating a specific scenario and exploiting OVM configuration. 
The documentation provides clear, easy-to-follow steps for replicating the Proof of Concept on your setup (even on a local laptop).

- [Rules-based POC](contrib/end2end/poc/rule_based_poc/README.md)
- [Insights based POC](contrib/end2end/poc/insight_based_poc/README.md)
- [OTel based POC](contrib/end2end/poc/otel_based_poc/README.md)


> Note: We have created a video demonstrating the *Insights based POC* in action. 
> It can be accessed [here](docs/videos/poc_v2_video.mp4).

   
> Note: We have created a blog demonstrating the *OTel based POC* 
> It can be accessed [here](https://medium.com/@eran.raichstein/master-observability-with-ovm-and-open-telemetry-1ddd266b022d).



## Insights based Proof of Concept Walkthrough

![](docs/images/pocv2.svg) 

The diagram above illustrates our setup for the Insights based proof of concept. 

We have two edge locations each equipped with a metric generator, metric collector, and the OVM Processor. The metric generator produces app and cluster metrics, which are periodically scrapped by the metric collector and then transformed by the processor. The central cloud location runs the metric aggregator and the Manager. At the beginning of the proof of concept, the user specifies the two rules:

- **Rule 1:** Applies to Processor 1 and requests to filter (whitelist) only the app metrics when edge location 1 experiences network stress.
- **Rule 2:** Applies to Processor 2 and requests to increase the frequency of cluster metrics when edge location 2 encounters erroneous conditions.

Apart from triggering transformations based on user defined rules,  we also have a **brain** (controller) component that aids users by suggesting rules for managing observability data. This controller possesses the capability to communicate with the manager to automatically configure these rules, streamlining the process and enhancing user experience. 


The proof of concept is built to showcase two main capabilities of the Observability Volume Manager. 
1. Automation: Users only define rules for managing observability data under different conditions and the Observability Volume Manager autonomously and dynamically monitors and enforces these transformations without requiring user intervention each time conditions are met. This eliminates the need for user intervention each time conditions are met, alleviating the burden of configuring individual processors at edge locations everytime.
2. Specificity: The Observability Volume Manager can enforce a transformation DAG on a subset of Edge locations. Additionally, within these edge locations, specific transformations can be applied to designated metrics only. This fine-granied control provides a level of specificity lacking in current observability systems.
3. Intelligent Pruning: The controller analyzes the metrics to provide insights on similarity of metrics. This can be used as a recommendation or trigger pruning of metrics for intelligent metric transformation.

More details on the proof of concept are explained [here](contrib/end2end/poc/insight_based_poc/README.md).

  




