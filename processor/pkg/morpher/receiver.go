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
	DAGNodes   []DAGNode   `yaml:"dag"`
}

type Processor struct {
	Type   string            `yaml:"type"`
	ID     string            `yaml:"id"`
	Metric map[string]string `yaml:"metrics"`
}

type DAGNode struct {
	ID       string   `yaml:"node"`
	Children []string `yaml:"children"`
}

func selectorsToString(selectors []Selector) string {
	template_string := `select distinct phash from labels where label = '%[1]s' and val = '%[2]s'`
	filled_strings := make([]string, len(selectors))
	for i, selector := range selectors {
		filled_strings[i] = fmt.Sprintf(template_string, selector.Key, selector.Value)
	}
	query_string := `phash in (` + strings.Join(filled_strings, " INTERSECT ") + ")" //multiple selectors
	log.Debug(query_string)
	return query_string
}

func (p Processor) ParseSelector() string {
	selectors := []Selector{Selector{Key: "__name__", Value: p.Metric["metric_name"]}}
	if p.Metric["condition"] != "" {
		conditions := strings.Split(p.Metric["condition"], "and")
		for _, condition := range conditions {
			condition = strings.TrimSpace(condition)
			key_value := strings.Split(condition, "=")
			selectors = append(selectors, Selector{key_value[0], key_value[1]})
		}
	}
	return selectorsToString(selectors)
}

func (p Processor) ParseParams() []float64 {
	params := []float64{}
	switch p.Type {
	case "aggregate":
	case "frequency":
		val, _ := strconv.ParseFloat(p.Metric["interval"], 32)
		params = append(params, val)
	}

	return params

}

func (p Processor) ParseProcessor() MorphUnit {
	// Validate that passed list of parameters matches against some fixed list (condition, metric_name, interval)
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
	w.WriteHeader(http.StatusOK)
	err := yaml.Unmarshal(bodyBytes, &request)
	if err != nil {
		http.Error(w, "Error parsing YAML", http.StatusBadRequest)
		error := fmt.Errorf("Error in decoding create request: unexpected YAML body: %s", err)
		log.Print(error)
	}

	log.Infof("Received body: %+v\n", request)

	// Do the processing
	morphNodes := make(map[string]*MorphNode)
	for _, processor := range request.Processors {
		morphNode := NewMorphNode(processor.ParseProcessor(), processor.ID)
		morphNodes[processor.ID] = morphNode
	}

	// Do the DAG formation
	root := m.NewRootNode()
	for _, DAGnode := range request.DAGNodes {
		morphNode, ok := morphNodes[DAGnode.ID]
		if !ok {
			error := fmt.Errorf("No node by id %s in list of processors", DAGnode.ID)
			http.Error(w, error.Error(), http.StatusBadRequest)
			log.Error(error)
			return
		}

		root.AddNodeChild(morphNode)
		for _, childID := range DAGnode.Children {
			child, ok := morphNodes[childID]
			if !ok {
				error := fmt.Errorf("No node by id %s in list of processors", childID)
				http.Error(w, error.Error(), http.StatusBadRequest)
				log.Error(error)
				return
			}
			morphNode.AddNodeChild(child)
		}
	}

	m.CompileMorph()
}

func (m *Morpher) Delete(w http.ResponseWriter, r *http.Request) {
	// Reset to default frequency of 30 sec for all
	def := NewMorphUnitFromString("frequency", "1", []float64{30000})
	root := m.NewRootNode()
	root.AddUnitChild(def)
	m.CompileMorph()
}
