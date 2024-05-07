# observ-vol-mgt: Observability Volume Manager
In today's dynamic computing landscape spanning centralized clouds, multi-cloud, and edge computing, the demand for adaptable observability is paramount. In particular, managing the volume of observability data is crucial.  With **Observability Volume Manager** we are introducing an automated, lightweight, SQL-based metric processing system, designed for distributed systems with multiple edge sites. 

## Overview
Observability Volume Manager provides a mechanism to perform various transformations to the metrics flows to manage the volume of metrics and support various edge deployment use cases.
The current implementation supports transformation of metrics defined in Prometheus format, where each metric comprises of metrics name and a set of labels in the form of key:value. PMF supports multiple transformations of metrics which can be represented as a DAG.

### Architecture: A Bird's Eye View
![](docs/images/architecture.svg)


### Terminology
- **Core**
  - The central cluster that is used to manage the edge clusters.
  - Can be an on-premise or cloud-based cluster.
  - There are no resources or network constraints expected in the core cluster.
  - There is a observability data aggregators (such as Prometheus, Thanos, Loki, etc.) running on the central cluster.
- **Edge**
  - This is an edge environment where the user workloads are running.
  - The edge environment is expected to have moderate yet constrained compute resources and network.
  - There is observability data collectors (such as OTel, Prometheus, Vector, etc.) running on the edge environment that are sending the data to the aggregator in the central cluster. 

### Use Case
The main objective in the current version is to demonstrate centralized control and management of observability data across all connected edge environments from the core. Users can specify transformation DAGs for individual edge locations through rules, which define conditions based on metrics collected from these environments. 

In upcoming versions, we plan to introduce a **brain** (controller) that will aid users by suggesting rules for managing observability data. This controller will possess the capability to communicate with the manager to automatically configure these rules, streamlining the process and enhancing user experience. 

## Folders Structure

### controller

The controller folder holds the code to centrally control the volume management

### contrib

The contrib folder holds various tools and scripts that helps to develop, build, and maintain the project

## Proof of Concept Walkthrough

## Running the Proof of Concept
