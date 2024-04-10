package transformer

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"sort"
	"time"

	"github.com/gogo/protobuf/proto"
	"github.com/golang/snappy"
	"github.com/thanos-io/thanos/pkg/store/labelpb"
	"github.com/thanos-io/thanos/pkg/store/storepb/prompb"

	"github.ibm.com/dynamic-freq/PMF/pkg/benchmarker"
)

type Transformer struct {
	// The target IP:port that is being reverse proxied for
	Target string
	// The IP:port to listen on for incoming connections
	Listen    string
	Transform func(prompb.WriteRequest, http.Header) prompb.WriteRequest
	// Function to be applied to headers
	TransformHeaders func(http.Header) http.Header
	// List of headers to be printed in the log
	LogHeaders []string
	Timings    benchmarker.Timings
}

// StandardizeLabels organizes the pb struct to conform to expected label patterns
func StandardizeLabels(wreq prompb.WriteRequest) prompb.WriteRequest {
	for i, ts := range wreq.Timeseries {
		sort.Slice(ts.Labels, func(i int, j int) bool {
			return ts.Labels[i].Name < ts.Labels[j].Name
		})

		// Set value for duplicate labels to empty string
		for i := 1; i < len(ts.Labels); i++ {
			if ts.Labels[i].Name == ts.Labels[i-1].Name {
				ts.Labels[i].Value = ""
				log.Printf("Duplicate label found: %s.\n", ts.Labels[i].Name)
			}
		}

		// Now, remove all empty entries
		var labels []labelpb.ZLabel
		for _, label := range ts.Labels {
			if label.Name != "" && label.Value != "" {
				labels = append(labels, label)
			} else {
				log.Printf("Empty label found: (%s, %s).\n", label.Name, label.Value)
			}
		}
		wreq.Timeseries[i].Labels = labels
	}

	return wreq
}

// NewProxy takes target host and creates a reverse proxy
func (txfm *Transformer) newProxy(targetHost string) (*httputil.ReverseProxy, error) {
	url, err := url.Parse(targetHost)
	if err != nil {
		return nil, err
	}

	proxy := httputil.NewSingleHostReverseProxy(url)

	originalDirector := proxy.Director
	proxy.Director = func(req *http.Request) {
		originalDirector(req)
		txfm.modifyRequest(req)
	}

	// proxy.ModifyResponse = modifyResponse()
	// proxy.ErrorHandler = errorHandler()
	return proxy, nil
}

func (txfm *Transformer) prepareLogHeaders(req *http.Request) string {
	logHeaders := "Headers{"
	if txfm.LogHeaders == nil {
		logHeaders += fmt.Sprintf("%v", req.Header)
	} else {
		for _, header := range txfm.LogHeaders {
			logHeaders += fmt.Sprintf("%s: %v,", header, req.Header[header])
		}
	}
	logHeaders += "}"

	return logHeaders
}

func (txfm *Transformer) modifyRequest(req *http.Request) {
	// logHeaders := txfm.prepareLogHeaders(req)

	reqBody, err := ioutil.ReadAll(req.Body)
	if err != nil {
		fmt.Printf("Error in reading: %v", err)
	}

	payload, err := snappy.Decode(nil, reqBody)
	if err != nil {
		fmt.Printf("Error in decoding: %v", err)
	}

	var wreq prompb.WriteRequest
	err = proto.Unmarshal(payload, &wreq)
	if err != nil {
		fmt.Printf("Error in unmarshalling: %v", err)
	}

	start := time.Now()
	uwreq := txfm.Transform(wreq, req.Header)
	uwreq = StandardizeLabels(uwreq)

	// Optionally modify headers (if TransformHeaders is provided)
	if txfm.TransformHeaders != nil {
		req.Header = txfm.TransformHeaders(req.Header)
	}
	elapsed := time.Since(start)

	payload2, err := proto.Marshal(&uwreq)
	if err != nil {
		fmt.Printf("Error in marshalling data: %v", err)
	}

	encoded := snappy.Encode(nil, payload2)
	if err != nil {
		fmt.Printf("Error in encoding data: %v", err)
	}
	// fmt.Printf("Request => %s -> [%v] in %s.\n", logHeaders, len(encoded), elapsed)
	if elapsed.Seconds() > 0.03 {
		txfm.Timings.AddTiming("E2E", elapsed) //differentitate from empty request which take 1 ms correct ones are ~300ms
	}

	req.Body = ioutil.NopCloser(bytes.NewBuffer(encoded))

	req.ContentLength = int64(len(encoded))
}

// proxyRequestHandler handles the http request using proxy
func proxyRequestHandler(proxy *httputil.ReverseProxy) func(http.ResponseWriter, *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		proxy.ServeHTTP(w, r)
	}
}

func healthCheck(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/plain")
	if _, err := w.Write([]byte("OK")); err != nil {
		log.Println("Error writing response for GET /health: ", err)
	}
}

func (txfm *Transformer) Start() {
	proxy, err := txfm.newProxy(txfm.Target)
	if err != nil {
		panic(err)
	}

	mux := http.NewServeMux()

	// health endpoint
	mux.HandleFunc("/health", healthCheck)
	// handle all requests to your server using the proxy
	mux.HandleFunc("/", proxyRequestHandler(proxy))
	log.Fatal(http.ListenAndServe(txfm.Listen, mux))
}
