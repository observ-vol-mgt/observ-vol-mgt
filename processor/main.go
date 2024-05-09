package main

import (
	"context"
	"flag"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"

	"github.com/ilyakaznacheev/cleanenv"
	"github.com/sirupsen/logrus"
	"github.com/thanos-io/thanos/pkg/store/storepb/prompb"
	rwt "github.ibm.com/dynamic-freq/PMF/pkg/transformer"
	"gopkg.in/yaml.v2"

	"github.ibm.com/dynamic-freq/PMF/pkg/benchmarker"
	"github.ibm.com/dynamic-freq/PMF/pkg/dbinterface"
	"github.ibm.com/dynamic-freq/PMF/pkg/morpher"
)

var log = logrus.New()

type Config struct {
	WindowSize  int    `yaml:"window" env:"WINDOW" env-default:6000`
	OutputDir   string `yaml:"outputdir" env:"OUTPUT"`
	DAGFunction string `yaml:"dag" env:"DAG"`
}

var cfg Config

type Mercury struct {
	Morpher morpher.Morpher
	DB      dbinterface.DB
	Queue   Queue
	Timings benchmarker.Timings
}

func NewMercury(cfg Config, timings benchmarker.Timings) *Mercury {
	return &Mercury{
		Morpher: morpher.NewMorpher(),
		DB:      dbinterface.InitDB(os.Stdout, timings),
		Queue: Queue{
			lastEmptied:  time.Now(),
			batchSize:    cfg.WindowSize,
			PendingBatch: make([]prompb.TimeSeries, 0, cfg.WindowSize),
		},
		Timings: timings,
	}
}

type Queue struct {
	batchSize    int
	PendingBatch []prompb.TimeSeries
	lock         sync.RWMutex
	lastEmptied  time.Time
}

func (m *Mercury) insertToQueue(wreq prompb.WriteRequest) int {
	m.Queue.PendingBatch = append(m.Queue.PendingBatch, wreq.Timeseries...)
	size := len(m.Queue.PendingBatch)
	return size
}

func (m *Mercury) Receive(wreq prompb.WriteRequest, header http.Header) prompb.WriteRequest {
	m.Queue.lock.Lock()
	size := m.insertToQueue(wreq)
	if size >= m.Queue.batchSize {
		log.Infof("Queue size: %d\n", size)
		// if (time.Since(m.Queue.lastEmptied).Seconds() >= 1 && size != 0) || size >= m.Queue.batchSize {
		// batch := m.Queue.PendingBatch[:m.Queue.batchSize]
		// m.Queue.PendingBatch = m.Queue.PendingBatch[m.Queue.batchSize:]
		m.DB.Insert(m.Queue.PendingBatch)
		m.Queue.PendingBatch = nil
		m.Queue.lastEmptied = time.Now()
		wreq.Timeseries = m.DB.Exec(m.Morpher)
		m.Queue.lock.Unlock()
		return wreq
	}
	m.Queue.lock.Unlock()
	wreq.Timeseries = nil
	return wreq
}

func (m *Mercury) cleanup(output_dir string) {
	log.Info("Cleaning up EMP")
	m.Timings.GetStats(output_dir)
	m.DB.CleanUp()
}

func readAndStoreConfig() {
	err := cleanenv.ReadConfig("./config.yml", &cfg)
	if err != nil {
		log.Fatalf("Error reading config")
	}

	log.Infof("%v", cfg)

	// Create OutputDir if not exists
	err = os.MkdirAll(cfg.OutputDir, os.ModePerm)

	// Write config file to OutputDir
	file, err := os.OpenFile(cfg.OutputDir+"/config.yml", os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalf("Error opening/creating file: %v", err)
	}
	defer file.Close()
	enc := yaml.NewEncoder(file)
	err = enc.Encode(cfg)
	if err != nil {
		log.Fatalf("error encoding: %v", err)
	}
}

func main() {
	var target = flag.String("target", "http://thanos_receive:19291", "Cortex/Thanos metrics endpoint")
	var listen = flag.String("listen", "0.0.0.0:8081", "Prometheus remote write listener endpoint")
	var morphport = flag.String("morpher", "0.0.0.0:8100", "DAG reader")
	flag.Parse()
	//readAndStoreConfig()

	// log.SetLevel(logrus.DebugLevel)

	timings := benchmarker.NewTimings()
	mercury := NewMercury(cfg, timings)
	//go mercury.Morpher.StartServerAndRegister(":8100")
	go mercury.Morpher.StartServerAndRegister(*morphport)

	// Create a context that is cancelled when an interrupt signal is received
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGINT, syscall.SIGHUP, syscall.SIGTERM)
	defer stop()

	// Run your program logic here
	txfm := rwt.Transformer{
		Target:     *target,
		Listen:     *listen,
		Transform:  mercury.Receive,
		LogHeaders: []string{"Content-Length"},
		Timings:    timings,
	}
	go func() {
		txfm.Start()
	}()

	// Wait until the context is done
	<-ctx.Done()

	// Call cleanup function
	//mercury.cleanup(cfg.OutputDir)

	// Exit the program
	os.Exit(1)
}
