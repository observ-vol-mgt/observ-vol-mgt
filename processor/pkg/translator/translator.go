//package main
package translator

/***

  Main DAG yaml transaltor package
*/

import (
        //"encoding/json"
        //"fmt"
        //"net/http"
        "strings"
        //"time"
        "io/ioutil"

        //"github.com/gorilla/mux"
        "github.com/sirupsen/logrus"
        "gopkg.in/yaml.v2"
        morpher "github.ibm.com/dynamic-freq/PMF/processor/pkg/morpher"
)

/*var data = `
processors:
  - type: filter
    metrics:
      metric_name: cluster_cpu_usage
      condition: cluster_id='wec1' and namespace_name='data-science'
      action: include/exclude
`*/
var log = logrus.New()

type DAGNode struct{
   Transformers []Transformer `yaml:"processors"`
}
type Transformer struct{
   m morpher.MorphUnit 
   s []morpher.Selector
   Type string `yaml:"type"`
   Metric struct{
   MetricName string `yaml:"metrics:metric_name"`
   Condition string `yaml:"condition"`
   Parameters []Parameter `yaml:",flow"`
   } `yaml:"metrics"`
}
type Parameter struct{
   Key string
   Value string
}
func (t Transformer) ParseSelector(){
      log.Println("Inparse")
      res1 := strings.Split(t.Metric.Condition, "and")
      for i := 0; i < len(res1); i++ {
           res2 := strings.Split(res1[i], "=")
           var s1 morpher.Selector
           s1.Key= res2[0]
           s1.Value = res2[1]
           t.s = append(t.s,s1)
           log.Println(t.s[i])
      }
      
}
func (t Transformer) FillMorph(){
      log.Println("Infill")
      t.m.Type = t.Type
      t.ParseSelector()
} 
func main() {
    result := DAGNode{}
    content, err := ioutil.ReadFile("../../../controller/dag_examples/filter.yaml")
    if err != nil {
        log.Fatal(err.Error())
        return
    }
    err = yaml.Unmarshal(content, &result)
    if err != nil {
        log.Fatal("Failed to parse file ", err)
    }
    result.Transformers[0].FillMorph()
    log.Println(result.Transformers[0].Metric.Condition)
}
