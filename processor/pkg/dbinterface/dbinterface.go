package dbinterface

import (
	"database/sql"
	"io"
	"os"
	"sync"
	"time"

	scan "github.com/blockloop/scan/v2"
	_ "github.com/mattn/go-sqlite3"
	"github.com/mitchellh/hashstructure/v2"
	"github.com/sirupsen/logrus"
	"github.com/thanos-io/thanos/pkg/store/labelpb"
	"github.com/thanos-io/thanos/pkg/store/storepb/prompb"
	// "golang.org/x/sync/errgroup"

	"github.ibm.com/dynamic-freq/PMF/pkg/benchmarker"
	"github.ibm.com/dynamic-freq/PMF/pkg/morpher"
)

var log = logrus.New()

const (
	CreateIndex string = `create index idx on metrics(phash)`
)

type PhashMap struct {
	Lock sync.RWMutex
	Map  map[string][]labelpb.ZLabel
}

type DB struct {
	db             *sql.DB
	phashMap       PhashMap
	timings        benchmarker.Timings
	CreateQueries  []*sql.Stmt
	InsertQueries  map[string]*sql.Stmt
	CleanUpQueries []string
}

func (DB *DB) PrepareStmt(query string) *sql.Stmt {
	stmt, err := DB.db.Prepare(query)
	if err != nil {
		log.Errorf("Error preparing statement for query %s: %s", query, err)
	}
	return stmt
}

func InitDB(f io.Writer, timings benchmarker.Timings) DB {
	os.Remove("./foo.db")
	// db, err := sql.Open("sqlite3", "foo.db?_journal=memory&cache=shared&_sync=off")
	db, err := sql.Open("sqlite3", "file::memory:?_journal=memory&cache=shared&_sync=off")
	// db, err := sql.Open("sqlite3", ":memory:")
	if err != nil {
		log.Fatal(err)
	}

	log.Out = f
	log.SetLevel(logrus.InfoLevel)

	DB := DB{
		db: db,
		phashMap: PhashMap{
			Map: make(map[string][]labelpb.ZLabel),
		},
		timings: timings,
	}

	DB.CreateQueries = []*sql.Stmt{
		DB.PrepareStmt(`create table metrics (phash text, timestamp integer, val integer, export boolean)`),
		DB.PrepareStmt(`create table labels (phash text, label text, val text)`),
		DB.PrepareStmt(`create table frequency (phash text, last integer)`),
	}

	DB.Create()
	DB.InsertQueries = map[string]*sql.Stmt{
		"labels":  DB.PrepareStmt("insert into labels(phash, label, val) values(?,?,?)"),
		"freq":    DB.PrepareStmt("insert into frequency(phash, last) values (?, 0)"),
		"metrics": DB.PrepareStmt("insert into metrics values (?,?,?,0)"),
	}
	DB.CleanUpQueries = []string{
		`delete from metrics`,
		`drop index if exists idx`,
	}

	return DB
}

func (DB *DB) CleanUp() {
	DB.db.Close()
}

func (DB *DB) timer(name string) func() {
	start := time.Now()
	return func() {
		DB.timings.AddTiming(name, time.Since(start))
		// log.Infof("%s took %v\n", name, time.Since(start))
	}
}

func (DB *DB) Create() {
	// defer DB.timer("create")()
	for _, stmt := range DB.CreateQueries {
		_, err := stmt.Exec()
		if err != nil {
			log.Printf("%q: %s\n", err, stmt)
			return
		}
	}
}

func (DB *DB) phash2(metric prompb.TimeSeries) string {
	hash, err := hashstructure.Hash(metric, hashstructure.FormatV2, nil)
	if err != nil {
		panic(err)
	}
	return string(hash)
}

func (DB *DB) phash(metric prompb.TimeSeries) string {
	phash := ""
	for _, label := range metric.Labels {
		phash += label.Name
		phash += label.Value
	}

	return phash
}

func (DB *DB) Insert(metrics []prompb.TimeSeries) {
	defer DB.timer("insert")()
	// t1 := time.Now()
	tx, err := DB.db.Begin()
	if err != nil {
		log.Errorf("Error beginning txn: %s\n", err)
		return
	}

	log.Infof("Inserting %d metrics into db\n", len(metrics))
	for _, m := range metrics {
		phash := DB.phash(m)

		// If first time, store phash to labels mapping and store labels in db
		DB.phashMap.Lock.Lock()
		_, ok := DB.phashMap.Map[phash]
		DB.phashMap.Lock.Unlock()
		if !ok {
			DB.phashMap.Lock.Lock()
			DB.phashMap.Map[phash] = m.Labels
			DB.phashMap.Lock.Unlock()

			for _, label := range m.Labels {
				_, err := DB.InsertQueries["labels"].Exec(phash, label.Name, label.Value)
				if err != nil {
					log.Errorf("Error inserting labels: %s", err)
					return
				}
			}

			_, err := DB.InsertQueries["freq"].Exec(phash) //dummy row timestamp 0 by default
			if err != nil {
				log.Errorf("Error inserting into frequency: %s", err)
			}
		}

		for _, sample := range m.Samples {
			_, err = DB.InsertQueries["metrics"].Exec(phash, sample.Timestamp, sample.Value)
			if err != nil {
				log.Errorf("Error inserting metrics: %s\n", err)
				return
			}
		}
	}

	for {
		err = tx.Commit()
		if err != nil {
			log.Errorf("Error committing txn: %s\n", err)
			continue
		}
		break
	}
	// t2 := time.Now()
	// DB.addTiming("insert-proc", t2.Sub(t1))
}

type QueryResult struct {
	Phash     string  `db:"phash"`
	Timestamp int64   `db:"timestamp"`
	Val       float64 `db:"val"`
}

func (DB *DB) QRtoLabels(qr []QueryResult) []prompb.TimeSeries {
	metrics := make([]prompb.TimeSeries, len(qr))
	DB.phashMap.Lock.Lock()
	for i, result := range qr {
		metrics[i] = prompb.TimeSeries{Labels: DB.phashMap.Map[result.Phash], Samples: []prompb.Sample{{Timestamp: result.Timestamp, Value: result.Val}}} //samples is array of timestamp and value
	}
	DB.phashMap.Lock.Unlock()
	return metrics
}

func ExecRecursively(node *morpher.MorphNode, tx *sql.Tx) {
	log.Debugf("Executing query: %s", node.Unit.Query)
	r, err := tx.Exec(node.Unit.Query)
	if err != nil {
		log.Errorf("Error executing: %s\n", err)
		return
	}
	rows, _ := r.RowsAffected()
	log.Infof("Query affected: %d\n", rows)
	for _, child := range node.Children {
		ExecRecursively(child, tx)
	}

	// log.Infof("Deletion query: %s", node.Unit.DeleteQuery)
	_, err = tx.Exec(node.Unit.DeleteQuery)
	if err != nil {
		log.Errorf("Error deleting: %s\n", err)
		return
	}
}

func (DB *DB) Exec(m morpher.Morpher) []prompb.TimeSeries {
	// defer DB.timer("Exec")()
	t1 := time.Now()
	tx, err := DB.db.Begin()
	if err != nil {
		log.Errorf("Error beginning txn: %s\n", err)
		return []prompb.TimeSeries{}
	}

	_, err = tx.Exec(CreateIndex) //make search query faster, index on a table
	if err != nil {
		log.Errorf("Error executing %s\n", err)
		return []prompb.TimeSeries{}
	}

	dag := m.DAG
	ExecRecursively(dag, tx)

	_, err = tx.Exec(m.DeleteQueries)
	if err != nil {
		log.Errorf("Error executing: %s\n", err)
	}

	t2 := time.Now()
	// Final export query
	rows, err := tx.Query("select phash, timestamp, val from metrics where export=1")
	if err != nil {
		log.Errorf("Error getting count: %s", err)
		return []prompb.TimeSeries{}
	}

	var results []QueryResult
	err = scan.Rows(&results, rows)
	if err != nil {
		log.Errorf("Error getting results: %s\n", err)
	}

	rows.Close()

	// Clean up
	for _, stmt := range DB.CleanUpQueries {
		_, err := tx.Exec(stmt)
		if err != nil {
			log.Errorf("Error performing clean up query %s: %s", stmt, err)
			return []prompb.TimeSeries{}
		}
	}

	err = tx.Commit()
	if err != nil {
		log.Errorf("Error committing txn: %s", err)
		return []prompb.TimeSeries{}
	}

	log.Infof("Exporting %d metrics\n", len(results))

	ts := DB.QRtoLabels(results)
	t3 := time.Now()
	DB.timings.AddTiming("exec", t2.Sub(t1))
	DB.timings.AddTiming("export", t3.Sub(t2))
	return ts
}
