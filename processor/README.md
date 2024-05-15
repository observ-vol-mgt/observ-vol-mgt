# Description of Architecture

There are 3 main components which make up the processor.
1. [`transformer`](./pkg/transformer)
2. [`morpher`](./pkg/morpher)
3. [`dbinterface`](./pkg/dbinterface)

Additionally, we have a component [`benchmarker`](./pkg/benchmarker) which is used to measure and store timings of each request at each component.

## Transformer

The transformer is a HTTP proxy which receives metrics in the [Prometheus Remote Write format](https://prometheus.io/docs/concepts/remote_write_spec/), calls a Transform function on the data and sends metrics in the Remote Write format.

It receives HTTP POST payloads containing metric data (encoded as Protobuf) from a `listen` address, converts it into the [`prompb`](https://pkg.go.dev/github.com/thanos-io/thanos/pkg/store/storepb/prompb) format to perform processing on the metrics (through the Transform function) and finally encodes the `prompb` back to HTTP payload and sends it to the `target` address. The `listen` and `target` address are set through the processor's flags.

## Morpher
The morpher manages the DAG chain and the compilation of the DAG from the user submitted format to the SQL query that needs to be executed. Users represent their processor DAG (more specifically a tree) as a yaml which is then compiled to build a set of interlinked SQL queries which use the previous DAG node output as input.

The morpher [receiver](./pkg/morpher/receiver.go) exposes 2 endpoints, `create` and `delete` to update the DAG, which are described [below](#processor-api-endpoints). It further parses the selector and parameters before passing it to the [morpher](./pkg/morpher/morpher.go).

## DBInterface

The `dbinterface` mainly deals with managing the Database throughout the processor's lifecycle by inserting metrics into the db, executing the SQL commands corresponding to the DAG and finally moving metrics which need to be exported, from the database.

SQLite offers 2 modes, file mode and in-memory mode for managing the DB.

# Processor API Endpoints
The processor exposes 2 endpoints to update DAGs dynamically at the `8100` port. This is the `/morphchain` endpoint with the `/create` and `/delete` endpoints for creating and deleting DAGs respectively.

To create a DAG, call the `create` endpoint with the DAG yaml as given in example `../contrib/processor_dag_examples/filter.yaml`

```
curl IP:8100/morphchain/create --data-binary '@controller/dag_examples/filter.yaml'
```

To reset the DAG, call the `delete` endpoint. This will reset to the default DAG, which sends all metrics at 30 sec frequency.

```
curl IP:8100/morphchain/delete
```

# Running locally

The architecture has 4 main components which we need to bring up to run the end to end system locally:
1. Metric source: To generate metrics in the Prometheus format. While a tool like Avalanche can be used, it does not allow customization of the number and style of labels. We have built a custom generator which allows to customize the labels, in [`ec-metric-gen`](../contrib/ec-metric-gen/).
2. Local metric collector: A metric collector agent which collects metrics from multiple metric sources and exposes it in the Prometheus Remote Write format. This could be Prometheus or some other tool. For further steps, we consider Prometheus.
3. Metric processor: This is the current repo. Compilation and running instructions are given below.
4. Central Metric collector: Metric collector agent which can receive from multiple metric collectors (in the Prometheus Remote Write format). Some tools for this are Thanos, Cortex or even Prometheus. For further steps, we consider Thanos.

Prometheus can be [installed and run locally ](https://prometheus.io/docs/prometheus/latest/getting_started/) or [run in a docker container](https://hub.docker.com/r/prom/prometheus). Similarly, Thanos can [be installed locally](https://github.com/thanos-io/thanos/releases) or [run in a docker container](https://quay.io/repository/thanos/thanos).

To compile the processor, run:
```
go build main.go
```

Running:
1. Start metric generator - we use the [`gen-metrics-gutentag.py`](../contrib/ec-metric-gen/gen-metrics-gutentag.py) script. For more details on the different options it provides, check its README. It exposes port 8000 for Prometheus to scrape metrics.
   ```
   $ cd ../contrib/ec-metric-gen/
   $ python3 gen-metrics-gutentag.py --fake --nmetrics 1000 --nlabels 10
   
   INFO:root:Generating 10 metrics excluding labels and 1000 metrics including labels
   ```
2. Start local metric collector. A sample Prometheus configuration is given [here](../contrib/ec-metric-gen/prometheus.yml). There are 2 main configurations:

	Setting the target to scrape from (the metric-gen prometheus scrape endpoint)
	
	```
	scrape_configs:
      static_configs:
		- targets: ["localhost:8000"]
    ```
	
	and the push URL. This is the processor's transformer endpoint.
	
	```
	remote_write:
	  - url: "http://localhost:8081/api/v1/receive"
    ```
	
	We run prometheus as:
	
	```
	$ prometheus --config.file="../contrib/ec-metric-gen/prometheus.yml"
	```
	
	Until the processor starts, prometheus may complain about connection being refused. Once the processor starts, it will start forwarding the metrics.
	
	```
	ts=2024-05-06T03:29:44.164Z caller=dedupe.go:112 component=remote level=warn remote_name=e5a93c url=http://localhost:8081/api/v1/push msg="Failed to send batch, retrying" err="Post \"http://localhost:8081/api/v1/push\": dial tcp [::1]:8081: connect: connection refused"
	```
3. Start the PMF processor. It takes 2 flags, one for the target (this is the Thanos/Cortex endpoint) and one for the listen (this is the endpoint which listens for Prometheus Remote Write pusher).

    Target needs to be configured based on the Central Metric Collector. Thanos listens on port `19291` and Cortex listens on port `9090`.
	
	```
	$ go run main.go --target http://localhost:19291" --listen "0.0.0.0:8081"
	```
4. Start Thanos. Thanos has the receive and query components which need to start up:
	```
	./thanos receive --grpc-address=0.0.0.0:10901 --remote-write.address=0.0.0.0:19291 --label=receive=\"true\"
	./thanos query --grpc-address=0.0.0.0:20901 --http-address=0.0.0.0:19192 --store=0.0.0.0:10901
	```


To visualize the metrics, you may additionally set up Grafana and connect to Thanos.
