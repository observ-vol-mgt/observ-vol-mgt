import argparse
import logging
from logging import exception
import random
import time
import yaml
import json
import gutenTAG.api as gt
from calendar import c
from flask import Flask, jsonify, request
from prometheus_client import start_http_server, Gauge
import uuid
import itertools
import threading

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

LENGTH = 1000
metrics = []
cluster_metrics = []
node_metrics = []
nw_metrics = []
app_metrics = []
app_nw_metrics = []

def read_yaml(yamlfile):
    with open(yamlfile, "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    logging.info("Successfully read yaml file: %s" % yamlfile)
    return data

def create_random_gutentag_ts():
    # curves = ["sine", "cylinder_bell_funnel", "square", "random_mode_jump"]
    curves = ["sine"]
    ampl = random.randint(40, 60)
    offset = random.randint(60, 100)
    #freq = random.random()/2 + 0.5
    freq = 5.0
    curve = random.sample(curves, 1)[0]
    if curve == "sine":
        return gt.sine(length=LENGTH, frequency=freq, amplitude=ampl) + offset
    elif curve == "cosine":
        return gt.cosine(length=LENGTH, frequency=freq, amplitude=ampl) + offset
    elif curve == "ecg":
        return gt.ecg(length=LENGTH, frequency=ampl) + offset
    elif curve == "cylinder_bell_funnel":
        pattern_length=random.randint(50, 100)
        return gt.cylinder_bell_funnel(length=LENGTH, avg_pattern_length = pattern_length, avg_amplitude = ampl) + offset
    elif curve == "square":
        return gt.square(length=LENGTH, frequency=freq, amplitude=ampl) + offset
    elif curve == "random_mode_jump":
        return gt.random_mode_jump(length=LENGTH, frequency=freq) + offset
    return [offset + random.randint(amplitude) for _ in range(LENGTH)]

def create_flat_gutentag_ts():
    offset = 100
    ampl = 60
    return [offset + ampl for _ in range(LENGTH)]

def create_fixed_gutentag_ts():
    #for  metrics with similarity
    # curves = ["sine", "cylinder_bell_funnel", "square", "random_mode_jump"]
    curves = ["sine"]
    ampl = 2
    #offset = random.randint(60,65) # small rate randomize
    offset = 60
    #freq = random.random()/2 + 0.5
    freq = 1
    #return [offset + ampl for _ in range(LENGTH)]
    return gt.sine(length=LENGTH, frequency=freq, amplitude=ampl) + offset

"""
Labels is an array of dicts
Since for every unique named metric, if only labels change we add it to the gauge by looping and calling gauge.labels() for every unique set of labels
So every dict is a unique set of labels

We only need to create a single Gauge for a uniquely named metric
We store different sets of unique label values since it is needed during "set" 
"""
def create_new_gutentag_metric(prefix, idx, labels,duplicate):
    g = Gauge("{0}_metric_{1}".format(prefix, idx), prefix + " Metric", labels[0].keys())
    if duplicate == "true":
        ts = [create_flat_gutentag_ts() for _ in labels]
    else:
        ts = [create_random_gutentag_ts() for _ in labels]
    return (g, ts, labels)

def create_duplicate_gutentag_metric(prefix, idx, labels):
    g = Gauge("{0}".format(prefix), prefix + " Metric", labels[0].keys())
    ts = [create_fixed_gutentag_ts() for _ in labels]
    return (g, ts, labels)

def create_fake_metric(prefix, idx, labels):
    g = Gauge("{0}_metric_{1}".format(prefix, idx), prefix + " Metric", labels[0].keys())
    return g, labels

def create_fake_metrics(total_metrics, nlabels, name="fake"):
    values = ["A", "B"]
    labels = [("label_{0}".format(i)) for i in range(nlabels)]
    iterables_list = [values for _ in range(nlabels)]
    combos = list(itertools.product(*iterables_list))
    all_labels = [dict(zip(labels, combo)) for combo in combos]
    n_all_labels = len(all_labels)
    n_labels_to_take = n_all_labels
    nmetrics = int(total_metrics/n_all_labels)

    # Too many labels, so reduce the number of labels by sampling
    if nmetrics < 10:
        nmetrics = 10
        n_labels_to_take = int(total_metrics/10)

    all_labels = random.sample(all_labels, n_labels_to_take)
    logging.debug(len(all_labels))
    nmetrics = int(total_metrics/len(all_labels))
    fake_metrics = []
    fake_metrics += [create_fake_metric(name, i, all_labels) for i in range(nmetrics)]
    #fake_metrics += [create_new_gutentag_metric("fake", i, all_labels) for i in range(nmetrics)]
    global metrics
    metrics = fake_metrics
    logging.info("Generating {0} metrics excluding labels and {1} metrics including labels".format(len(metrics), len(metrics) * len(metrics[0][1])))

def create_all_gutentag_metrics(conf_file, duplicate, opt_config=None):
    config = read_yaml(conf_file)
    cluster_name = opt_config['name'] if opt_config is not None else config['name']
    num_cluster_metrics = config['clusters']['num_metrics']

    # Create cluster metrics
    labels = {"cluster": cluster_name}
    global cluster_metrics
    cluster_metrics += [create_new_gutentag_metric("cluster", idx, [{"cluster": cluster_name, "metadata": str(uuid.uuid1()), "uid": str(uuid.uuid1())}],duplicate) for idx in range(num_cluster_metrics)]

    # Create hardware metrics
    num_hardware_metrics = config['hardware']['num_metrics']
    num_nodes = config['hardware']['num_nodes']
    
    global node_metrics
    node_metrics += [create_new_gutentag_metric("cluster_hardware",
                                   idx,
                                   [{"cluster": cluster_name, "metadata": str(uuid.uuid1()), "uid": str(uuid.uuid1()), "node": node} for node in range(num_nodes)],duplicate)
        for idx in range(num_hardware_metrics)]
    # Create cluster network metrics
    global nw_metrics
    
    if duplicate == "true":
        nw_metrics += [create_duplicate_gutentag_metric("k8s_pod_network_bytes",
                                    0,
                                    [{"cluster": cluster_name, "metadata": str(uuid.uuid1()), "uid": str(uuid.uuid1()), "namespace":"5G", "pod": "nwdaf-0", "node": 0}])]

    # Create application metrics
    num_apps = len(config['apps'])
    global app_metrics
    global app_nw_metrics
    for app in range(num_apps):
        app_name = config['apps'][app]['name']
        num_app_metrics = config['apps'][app]['num_metrics']
        network_metrics = int(num_app_metrics/5)        
        app_metrics += [create_new_gutentag_metric("app_" + str(app_name) + "_network", idx, [{"cluster": cluster_name, "metadata": str(uuid.uuid1()), "uid": str(uuid.uuid1()),"app": app_name, "IP": id} for id in ["192.168.1.1", "192.168.1.2", "192.168.1.3"]],duplicate) for idx in range(network_metrics)]
        app_metrics += [create_new_gutentag_metric("app_" + str(app_name), idx, [{"cluster": cluster_name,"metadata": str(uuid.uuid1()), "uid": str(uuid.uuid1()), "app": app_name}],duplicate) for idx in range(num_app_metrics)]
    if duplicate == "true":
            app_nw_metrics += [create_duplicate_gutentag_metric("nwdaf_5G_network_utilization", 0 , [{"cluster": cluster_name, "metadata": str(uuid.uuid1()), "uid": str(uuid.uuid1()),"app": "analytic_function", "namespace":"5G", "address": "192.168.1.1"}])]
    global metrics
    metrics = cluster_metrics + node_metrics + app_metrics + app_nw_metrics + nw_metrics
    logging.info("Generating {0} metrics excluding labels and {1} metrics including labels".format(len(metrics), len(metrics) * len(metrics[0][1])))

def set_metrics_runner(fake=True):
    counter = 0
    logging.info("set runner_Called")
    if fake:
        #logger.info("set runner {0}", metrics)
        while(True):
            time.sleep(5)
            for (g, label_array) in metrics:
                for labels in label_array:
                    val = random.randint(1, 100)
                    g.labels(**labels).set(val)
    else:
        #logging.info("set runner metrics", metrics)
        while(True):
            counter = (counter+1)%LENGTH
            time.sleep(5)
            for (g, ts_array, label_array) in metrics:
                for (ts, labels) in zip(ts_array, label_array):
                    g.labels(**labels).set(ts[counter])

# This function translates the json to determine the metrics which need to be changed and calls 
# action() function defined above for the chosen metrics
#currently not done for fake metrics
def change_metrics(r_data,isSet):
    change_metrics_list = []
    global metrics
    for nr_data in r_data.get('metrics'):
        metric_name = nr_data.get('name') + "_" + "_".join(str(t) for t in nr_data.get('type')) + "_" + "metric_" + "_".join(str(i) for i in nr_data.get('index'))
        change_metrics_list.append(metric_name)
        print(change_metrics_list)
    #TODO store metric_name as an array and change the inner if loop below
    #for (g, ts_array, label_array) in metrics: 
    for metric_name in change_metrics_list:
       for i, (g, ts_array, label_array) in enumerate(metrics):
            if g._name == metric_name:
                print("metric found")
                print(g)
                #change_metrics_list += (g, ts_array, label_array)
                if isSet:
                    new_ts_array = [x+200 for x in ts_array]
                else:
                    new_ts_array = [x-200 for x in ts_array]
                metrics[i] = (g, new_ts_array, label_array)
                    
            #for (ts, labels) in zip(ts_array, label_array):
            #    ts = [x+200 for x in ts]

    return "Metrics updated", 200
    
## To handle the json using flask
@app.route('/', methods=['POST'])
def update():
    rule_data = request.get_data()
    try:
        r_data = yaml.safe_load(rule_data)
    except Exception as e:
        logger.error("Invalid yaml data")
        return {"message":"Invalid YAML data"}, 400
    if r_data.get('action')=="SET":
        return change_metrics(r_data, True)
    elif r_data.get('action')=="RESET":
        return change_metrics(r_data, False)
    #elif record['type']=="SET ALL":
    #    return change_all_metrics(True)
    #elif record['type']=="RESET ALL":
    #    return change_all_metrics(False)
    else:
        return "Incorrect request type", 400

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Metrics generator")
    parser.add_argument('--conf', dest='conf', help='Config yaml file', default='conf.yaml')
    # Additional config - overrides config.yaml
    parser.add_argument('-n', '--name', dest='name', help='Name of the cluster', default='c0')
    parser.add_argument('-p', '--port', dest='port', help='Port to run http server for metrics', default=8000, type=int)
    parser.add_argument('-cp', '--clientport', dest='clientport', help='Port to run http server for reconfiguration', default=5002, type=int)
    parser.add_argument('-d', '--duplicate', dest='duplicate', help='Should app network metric be duplicate of cluster network metric', default='false')
    # To create artificial metrics with as many labels as we want
    parser.add_argument('--fake', dest='fake', action='store_true')
    parser.add_argument('--nmetrics', dest='nmetrics', default=1000, type=int)
    parser.add_argument('--nlabels', dest='nlabels', default=10, type=int)
    args = parser.parse_args()

    opt_config = {
        'name': args.name
    }
    
    if not args.fake:
        create_all_gutentag_metrics(args.conf, args.duplicate, opt_config)
    else:
        create_fake_metrics(args.nmetrics, args.nlabels, args.name)
                            
    # Start the gen-metrics interface
    #app.run(debug=False)
    
    # Start the prometheus server
    start_http_server(args.port)
    threading.Thread(target=lambda:app.run(host="0.0.0.0", port=args.clientport, debug=False)).start()
    set_metrics_runner(args.fake)
    

