go get github.com/ilyakaznacheev/cleanenv
go get github.com/sirupsen/logrus
go get github.com/thanos-io/thanos/pkg/store/storepb/prompb
go get github.ibm.com/dynamic-freq/PMF/processor/pkg/dbinterface
go get github.ibm.com/dynamic-freq/PMF/processor/pkg/morpher
go get github.ibm.com/dynamic-freq/PMF/processor/pkg/transformer
go get github.ibm.com/dynamic-freq/PMF/processor/pkg/benchmarker

For a local setup:
1. Install Prometheus
2. Install Thanos

Running:
1. Start thanos receive and thanos query
   `./thanos receive --grpc-address=0.0.0.0:10901 --remote-write.address=0.0.0.0:19291 --label=receive=\"true\"`
   `./thanos query --grpc-address=0.0.0.0:20901 --http-address=0.0.0.0:19192 --store=0.0.0.0:10901`
2. Start prometheus 
   `./prometheus --config.file="ec-metric-gen/prometheus.yml"`
3. Start PMF processor
   `go run main.go`
4. Start metric load-gen (ec-metric-gen):
   `python3 gen-metrics-gutentag.py --fake --nmetrics 100 --nlabels 10`
