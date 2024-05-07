package morpher

/***
  Main Transformation package
*/

import (
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/gorilla/mux"
	"github.com/sirupsen/logrus"
)

var log = logrus.New()

// If temp.view is not used, gives error that the temp table is not found

const (
	RootParent string = `metrics`
	RootQuery  string = `create temporary table t%[1]d as select phash, timestamp, val from metrics;`

	Prefix string = `create temporary table t%[1]d `

	UnitMorph     string = Prefix + ` as select phash, timestamp, val from %[2]s;`
	SelectorMorph string = Prefix + ` as select phash, timestamp, val from %[2]s where phash in %[3]s;`
	FilterMorph   string = Prefix + ` as select phash, timestamp, val from %[2]s where %[3]s;`
	FreqMorph     string = `create view temp.freq_v%[1]d(phash, timestamp, val) as select phash, max(timestamp), val from %[2]s where %[3]s group by phash;` + Prefix + ` as select temp.freq_v%[1]d.phash, timestamp, val from frequency join freq_v%[1]d on frequency.phash = temp.freq_v%[1]d.phash where timestamp >= frequency.last + %[4]f;drop view temp.freq_v%[1]d;
update frequency set last = (select case when count(*) > 0 then (select timestamp from t%[1]d where t%[1]d.phash = frequency.phash) else last end from t%[1]d);`
	ProbFreqMorph string = Prefix + ` as select phash, timestamp, val from (select phash, timestamp, val from %[2]s where %[3]s) where abs(CAST(random() AS REAL))/9223372036854775808 < 5000/%[4]f;`
	//ProbFreqMorph       string = Prefix + ` as select phash, timestamp, val from (select phash, timestamp, val, max(timestamp) - min(timestamp) as diff, count(*) as c from %[2]s where %[3]s group by phash) where abs(CAST(random() AS REAL))/9223372036854775808 < diff/((c-1)*%[4]f);`
	SimpleAdaptiveMorph string = Prefix + ` as select phash, timestamp, val from %[2]s where %[3]s and val >= %[4]f;`
	AggregateMorph      string = Prefix + ` as select phash, avg(timestamp) as timestamp, avg(val) as val from %[2]s where %[3]s group by phash; insert into metrics select phash, timestamp, val, 0 from t%[1]d;`
	DropMorph           string = ``

	LeafNode    string = `update metrics set export = 1 where (phash, timestamp, val) in (select phash, timestamp, val from %[1]s);`
	DeleteTable string = `drop table if exists t%d;`
	DeleteView  string = `drop view if exists t%d;`
)

var DefaultMorph string = strings.Replace(ProbFreqMorph, "%[3]s", "phash not in (select distinct phash from labels where %[3]s)", 1)

var StringToMorphMap = map[string]string{
	"frequency": ProbFreqMorph,
}

type MorphUnit struct {
	Type        string
	Selector    string
	Parameters  []float64
	Query       string
	DeleteQuery string
}

type Selector struct {
	Key   string
	Value string
}

func NewMorphUnit(typ string, selectors []Selector, parameters []float64) MorphUnit {
	mu := MorphUnit{
		typ, selectorsToString(selectors), parameters, "", "",
	}
	return mu
}

func NewMorphUnitFromString(typ string, selector string, parameters []float64) MorphUnit {
	mu := MorphUnit{
		typ, selector, parameters, "", "",
	}
	return mu
}

func (mu *MorphUnit) CompileQuery(parent string, id int, leaf bool) {
	log.Debugf("Type: %s\n", mu.Type)
	baseString := ""
	deleteQuery := DeleteTable
	exportSearchTable := fmt.Sprintf("t%d", id)
	switch mu.Type {
	case "frequency":
		baseString = ProbFreqMorph
	case "unit":
		baseString = UnitMorph
	case "selector":
		baseString = SelectorMorph
	case "root":
		baseString = RootQuery
	case "default":
		baseString = DefaultMorph
	case "adaptive":
		baseString = SimpleAdaptiveMorph
	case "aggregate":
		baseString = AggregateMorph
	case "filter":
		baseString = FilterMorph
	case "drop":
		baseString = DropMorph
		exportSearchTable = parent
	}

	values := make([]interface{}, len(mu.Parameters)+3)
	values[0] = id
	values[1] = parent
	values[2] = mu.Selector

	for i, p := range mu.Parameters {
		values[i+3] = p
	}

	mu.Query = fmt.Sprintf(baseString, values...) // 1 is name of table, 2 is name of parent table, 3 is selector, this is to create temp table suffixed with t(name of the table)

	if mu.Type == "drop" {
		mu.Query = baseString
	} else if leaf {
		// t := fmt.Sprintf(LeafNode, id)
		// log.Debugf("Leaf string: %s\n", t)
		mu.Query += fmt.Sprintf(LeafNode, exportSearchTable)
	}

	mu.DeleteQuery = fmt.Sprintf(deleteQuery, id)
	log.Info(mu.Query)
}

type MorphNode struct {
	ID       string
	Unit     MorphUnit
	Children []*MorphNode
}

func NewMorphNode(unit MorphUnit, ID ...string) *MorphNode {
	id := ""
	if len(ID) > 0 {
		id = ID[0]
	}

	node := MorphNode{
		ID:       id,
		Unit:     unit,
		Children: []*MorphNode{},
	}
	return &node
}

func (m *Morpher) NewRootNode() *MorphNode {
	rootNode := NewMorphNode(NewMorphUnitFromString("root", "", []float64{}))
	m.DAG = rootNode
	return rootNode
}

func (m *MorphNode) AddUnitChild(unit MorphUnit) {
	node := NewMorphNode(unit)
	m.Children = append(m.Children, node)
}

func (m *MorphNode) AddNodeChild(node *MorphNode) {
	m.Children = append(m.Children, node)
}

type MorphDAG *MorphNode

type Morpher struct {
	DAG           MorphDAG
	Counter       int
	DeleteQueries string
}

func createDefaultQuery(selectors []string) string {
	union_stmt := strings.Join(selectors, " or phash in ")
	log.Debugf(union_stmt)
	return union_stmt
}

func (m *Morpher) getNewID() int {
	id := m.Counter
	m.Counter++
	return id
}

func (m *Morpher) CompileMorphsRecursively(node *MorphNode, parent string) {
	id := m.getNewID()
	log.Info(node.ID)
	if len(node.Children) == 0 {
		// Leaf node => set as export
		node.Unit.CompileQuery(parent, id, true)
	} else {
		// Non-leaf node => create a view
		node.Unit.CompileQuery(parent, id, false)
		selectors := make([]string, len(node.Children))

		cur_table := fmt.Sprintf("t%d", id)

		for i, child := range node.Children {
			selectors[i] = child.Unit.Selector
			m.CompileMorphsRecursively(child, cur_table)
		}

		// No default sibling for unit node
		if len(selectors) == 1 && node.Children[0].Unit.Type == "unit" {
			return
		}

		// No default if child's selector is 1 (select all)
		if len(node.Children) > 0 && node.Children[0].Unit.Selector == "1" {
			return
		}

		// No default if child is filter
		if len(node.Children) > 0 && node.Children[0].Unit.Type == "filter" {
			return
		}

		// Creating and adding a new child with the Default Type and reverse query
		defaultUnit := NewMorphUnitFromString("default", createDefaultQuery(selectors), []float64{30000})
		defaultUnit.CompileQuery(cur_table, m.getNewID(), true)
		node.AddUnitChild(defaultUnit)
	}
}

func (m *Morpher) CompileMorph() {
	m.CompileMorphsRecursively(m.DAG, "")
}

func NewMorpher() Morpher {
	morpher := Morpher{Counter: 0}
	morpher.CreateTestChain()
	return morpher
}

func (m *Morpher) StartServerAndRegister(addr string) {
	r := mux.NewRouter()
	r.HandleFunc("/morphchain/create", m.Create)
	r.HandleFunc("/morphchain/delete", m.Delete)
	log.Fatal(http.ListenAndServe(addr, r))
}

func (m *Morpher) CreateTestChain() {
	rootNode := m.NewRootNode()
	// m.testDAG(rootNode, 15, "chain")
	// m.testNSelectors(rootNode, 2)
	m.testFrequency(rootNode)
	start := time.Now()
	m.CompileMorph()
	log.Info("Time to compile: ", time.Since(start))
	// m.DeleteQueries = DeleteQueries
}

func (m *Morpher) testUnit(rootNode *MorphNode) {
	unit := NewMorphUnitFromString("unit", "", []float64{})
	rootNode.AddUnitChild(unit)
}

func (m *Morpher) testDefault(rootNode *MorphNode) {
	unit := NewMorphUnit("selector", []Selector{{Key: "app", Value: "A"}}, []float64{})
	rootNode.AddUnitChild(unit)
}

func (m *Morpher) testFrequency(rootNode *MorphNode) {
	unit := NewMorphUnitFromString("frequency", "1", []float64{30000})
	// unit := NewMorphUnit("frequency", []Selector{{Key: "label_1", Value: "A"}}, []float64{30000})
	rootNode.AddUnitChild(unit)
}

func (m *Morpher) testNSelectors(rootNode *MorphNode, nselectors int) {
	selectors := []Selector{}
	for i := 0; i < nselectors; i++ {
		selectors = append(selectors, Selector{Key: fmt.Sprint("label_", i), Value: "A"})
	}

	unit := NewMorphUnit("freq", selectors, []float64{30000})
	rootNode.AddUnitChild(unit)
}

func (m *Morpher) testDAG(rootNode *MorphNode, nnodes int, dagtype string) {
	// Chain
	parentNode := rootNode
	if dagtype == "chain" {
		for i := 0; i < nnodes; i++ {
			node := NewMorphNode(NewMorphUnit("freq", []Selector{{Key: fmt.Sprint("label_", i), Value: "A"}}, []float64{30000}))
			parentNode.AddNodeChild(node)
			parentNode = node
		}
	} else if dagtype == "parallel" {
		for i := 0; i < nnodes; i++ {
			node := NewMorphNode(NewMorphUnit("freq", []Selector{{Key: fmt.Sprint("label_", i), Value: "A"}}, []float64{30000}))
			parentNode.AddNodeChild(node)
		}
	}
}

func (m *Morpher) testChain(rootNode *MorphNode) {
	node := NewMorphNode(NewMorphUnit("selector", []Selector{{Key: "app", Value: "A"}}, []float64{}))
	node.AddUnitChild(NewMorphUnitFromString("freq", "1", []float64{10000}))
	rootNode.AddNodeChild(node)
}

func (m *Morpher) testAdaptive(rootNode *MorphNode) {
	unit := NewMorphUnit("adaptive", []Selector{{Key: "label_0", Value: "A"}}, []float64{30})
	rootNode.AddUnitChild(unit)
}

func (m *Morpher) testAggregate(rootNode *MorphNode) {
	unit := NewMorphUnit("aggregate", []Selector{{Key: "label_0", Value: "A"}}, []float64{})
	rootNode.AddUnitChild(unit)
}

func (m *Morpher) testDrop(rootNode *MorphNode) {
	unit := NewMorphUnit("drop", []Selector{{Key: "label_0", Value: "A"}}, []float64{})
	rootNode.AddUnitChild(unit)
}

func (m *Morpher) testSelector(rootNode *MorphNode) {
	unit := NewMorphUnit("selector", []Selector{{Key: "label_0", Value: "A"}}, []float64{})
	rootNode.AddUnitChild(unit)
}

func (m *Morpher) testIntersect(rootNode *MorphNode) {
	rootNode.AddUnitChild(NewMorphUnit("drop", []Selector{{Key: "app", Value: "A"}, {Key: "cluster", Value: "1"}}, []float64{}))
	rootNode.AddUnitChild(NewMorphUnit("drop", []Selector{{Key: "app", Value: "B"}, {Key: "cluster", Value: "1"}}, []float64{}))
}
