package benchmarker

import (
	"fmt"
	"os"
	"time"

	"github.com/montanaflynn/stats"
	"github.com/orcaman/concurrent-map"
	"github.com/sirupsen/logrus"
)

var log = logrus.New()

type Time struct {
	start    time.Time
	end      time.Time
	duration time.Duration
}

type Timings struct {
	Map cmap.ConcurrentMap
}

func NewTimings() Timings {
	return Timings{
		cmap.New(),
	}
}

func (t *Timings) AddTiming(name string, time time.Duration) {
	timings, _ := t.Map.Get(name)
	ts := []float64{}
	if timings != nil {
		ts = timings.([]float64)
	}

	t.Map.Set(name, append(ts, time.Seconds()))
	// fmt.Printf("%s, %.3f\n", name, time.Seconds())
}

func (t *Timings) GetStats(output_dir string) {
	names := []string{"insert", "exec", "export", "E2E"}
	statistics := []string{"mean", "stdev"}
	files := make([]*os.File, len(statistics))

	for i, stat := range statistics {
		f, err := os.OpenFile(output_dir+"/latency_"+stat+".csv", os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0644)
		if err != nil {
			log.Fatal(err)
		}
		defer f.Close()
		files[i] = f
	}

	for _, name := range names {
		// Discard the first entries in the timings array
		ts, _ := t.Map.Get(name)
		timings := []float64{}
		if ts == nil {
			log.Errorf("nil map for %s\n", name)
		} else {
			timings = ts.([]float64)
		}
		log.Info(len(timings))
		if len(timings) > 3 {
			timings = timings[3:]
			for i, stat := range statistics {
				var value float64
				var err error
				if stat == "mean" {
					value, err = stats.Mean(stats.LoadRawData(timings))
				} else if stat == "stdev" {
					value, err = stats.StandardDeviation(stats.LoadRawData(timings))
				}
				if err != nil {
					log.Errorf("Error calculating mean: %s\n", err)
				}

				fmt.Printf("%s, %s, %.3f\n", name, stat, value)
				fmt.Fprintf(files[i], "%.3f,", value)
			}
		}
	}
	for i, _ := range files {
		fmt.Fprintf(files[i], "\n")
	}
}
