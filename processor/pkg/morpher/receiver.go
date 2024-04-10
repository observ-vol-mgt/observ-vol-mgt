package morpher

/***
  Receives and translates DAG creation requests
*/

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"strconv"
	"strings"

	"gopkg.in/yaml.v2"
)

/*
var data = `
processors:
  - type: filter
    metrics:
    metric_name: cluster_cpu_usage
    condition: cluster_id=wec1 and namespace_name=data-science
    action: include/exclude

`
*/
type ReceiverRequest struct {
	Processors []Processor `yaml:"processors"`
}

type Processor struct {
	Type   string `yaml:"type"`
	Metric struct {
		MetricName string            `yaml:"metrics:metric_name"`
		Condition  string            `yaml:"condition"`
		Parameters map[string]string `yaml:",flow"`
	} `yaml:"metric"`
}

func selectorsToString(selectors []Selector) string {
	template_string := `select distinct phash from labels where label = '%[1]s' and val = '%[2]s'`
	filled_strings := make([]string, len(selectors))
	for i, selector := range selectors {
		filled_strings[i] = fmt.Sprintf(template_string, selector.Key, selector.Value)
	}
	query_string := `(` + strings.Join(filled_strings, " INTERSECT ") + ")" //multiple selectors
	log.Info(query_string)
	return query_string
}

func (p Processor) ParseSelector() string {
	if p.Metric.Condition != "" {
		var selectors []Selector
		conditions := strings.Split(p.Metric.Condition, "and")
		for _, condition := range conditions {
			condition = strings.TrimSpace(condition)
			key_value := strings.Split(condition, "=")
			selectors = append(selectors, Selector{key_value[0], key_value[1]})
		}
		return selectorsToString(selectors)
	}
	return ""
}

func (p Processor) ParseParams() []float64 {
	params := []float64{}
	switch p.Type {
	case "freq":
		val, _ := strconv.ParseFloat(p.Metric.Parameters["frequency"], 32)
		params = append(params, val)
	}

	return params

}

func (p Processor) ParseProcessor() MorphUnit {
	return MorphUnit{
		Type:       p.Type,
		Parameters: p.ParseParams(),
		Selector:   p.ParseSelector(),
	}
}

// Receives an input of a morphchain
func (m *Morpher) Create(w http.ResponseWriter, r *http.Request) {
	// Read request body
	var bodyBytes []byte
	if r.Body != nil {
		bodyBytes, _ = ioutil.ReadAll(r.Body)
	}

	// Decode Request
	request := ReceiverRequest{}
	err := yaml.Unmarshal(bodyBytes, &request)
	if err != nil {
		http.Error(w, "Error parsing YAML", http.StatusBadRequest)
		error := fmt.Errorf("Error in decoding create request: unexpected YAML body: %s", err)
		log.Print(error)
	}

	log.Debugf("Received body: %+v\n", request)

	rootNode := m.NewRootNode()
	parentNode := rootNode
	for _, processor := range request.Processors {
		node := NewMorphNode(processor.ParseProcessor())
		// For now assuming parallel processors
		parentNode.AddNodeChild(node)
	}

	m.CompileMorph()
}
