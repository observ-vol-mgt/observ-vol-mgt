import argparse
import logging
from logging import exception
import random
import time
import yaml
import json
from calendar import c
from flask import Flask, jsonify, request
from prometheus_client import start_http_server, Gauge

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

def read_yaml(yamlfile):
    with open(yamlfile, "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    logging.info("Successfully read yaml file: %s" % yamlfile)
    return data

def create_cluster_metrics(nummetrics):
    g = [0]*nummetrics
    for i in range(nummetrics):
        g[i] =  Gauge("cluster_metric_"+str(i), "Cluster Metric", ['cluster'])
        g[i].labels(cluster=clusterName)
    return g

def create_hardware_metrics(nummetrics):
    g = dict()
    for j in range(len(nodeNames)):
        g[str(j)] = []
    for i in range(nummetrics):
        h = Gauge("cluster_hardware_metric_"+str(i), "Hardware Metric of Node", ['cluster', 'node'])
        for j in range(len(nodeNames)):
            h.labels(cluster = clusterName, node = str(j))
            g[str(j)].append(h)
    return g

def create_app_metrics(nummetrics):
    g = dict()
    for i in range(len(nummetrics)):
        h = [0]*nummetrics[i]
        for j in range(nummetrics[i]): 
            h[j] =  Gauge("cluster_app_"+str(appNames[i])+"_metric_"+str(j), "Application Metric", ['cluster', 'app'])
            h[j].labels(cluster = clusterName, app = appNames[i])
        g[appNames[i]] = h
    return g
    
## Creation of Metrics is defined as a separate function 
def create_all_metrics(conf_file, opt_config=None):
    global clusterMetrics, hardwareMetrics,appMetrics, clusterName, nodeNames, appNames, numAppMetrics
    config = read_yaml(conf_file)
    clusterName = opt_config['name'] if opt_config is not None else config['name']
    numClusterMetrics = config['clusters']['num_metrics']
    clusterMetrics = create_cluster_metrics(numClusterMetrics)
    numHardwareMetrics = config['hardware']['num_metrics']
    numNodes = config['hardware']['num_nodes']
    nodeNames = [str(i) for i in range(numNodes)]
    hardwareMetrics = create_hardware_metrics(numHardwareMetrics)
    numApps = len(config['apps'])
    appNames = []
    numAppMetrics = []
    for i in range(numApps):
        appNames.append(config['apps'][i]['name'])
        numAppMetrics.append(config['apps'][i]['num_metrics'])
    appMetrics = create_app_metrics(numAppMetrics)



# This function resets all metrics to zero irrespective of their states. 
# This might be required in case multiple anomalies are active.
def change_all_metrics(isSet):
    value = int(isSet)
    logging.debug(value)
    for i in range(len(clusterMetrics)):
        g = clusterMetrics[i].labels(clusterName)
        #g.set(value)
        g.set(200)
    for key,val in hardwareMetrics.items():
        if key in nodeNames:
            for j in range(len(val)):
                g = hardwareMetrics[key][j].labels(clusterName,key)
                #g.set(value)
                g.set(10)
        else:  
            return "Invalid node name", 400
    for key,val in appMetrics.items():
        if key in appNames:
            for j in range(len(val)):
                g = appMetrics[key][j].labels(clusterName,key)
                #g.set(value)
                g.set(10)
        else:
            return "Invalid application name", 400
    return "Metrics updated", 200


# This function sets a metric to 1 if isSet = True, otherwise resets it to zero
# def action(metric, isSet):
#     if isSet:
#         metric.set(int(isSet))
#     else:
#         metric.set(0)
#     return metric



# This function translates the json to determine the metrics which need to be changed and calls 
# action() function defined above for the chosen metrics
def change_metrics(clusterlist,isSet):
    for i in range(len(clusterlist)):
        element = clusterlist[i]
        if element['name'] == clusterName:
            clusterMetricIDs = [int(j) for j in element['clustermetrics']]
            for id in clusterMetricIDs:
                try:
                    g = clusterMetrics[id].labels(clusterName)
                    g.set(int(isSet))
                except:
                    return "Invalid cluster metric - update failed", 400
            clusterNodes = element['node']
            for k in range(len(clusterNodes)):
                node = clusterNodes[k]
                nodeName = node['name']
                if nodeName in nodeNames:
                    nodeMetricIDs = [int(j) for j in node['nodemetrics']]
                    for id in nodeMetricIDs:
                        try:
                            g = hardwareMetrics[nodeName][id].labels(clusterName, nodeName)
                            g.set(int(isSet))
                        except:
                            return "Invalid hardware metric - update failed", 400
                else:
                    return "Invalid node name", 400
            clusterApps = element['app']
            for l in range(len(clusterApps)):
                app = clusterApps[l]
                appName = app['name']
                if appName in appNames:
                    appMetricIDs = [int(j) for j in app['appmetrics']]
                    for id in appMetricIDs:
                        try:
                            g = appMetrics[appName][id].labels(clusterName, appName)
                            g.set(int(isSet))
                        except:
                            return "Invalid application metric - update failed", 400   
                else:
                    return "Invalid application name", 400 
            return "Metrics updated", 200
    return "Invalid cluster name", 400


## To handle the json using flask
@app.route('/', methods=['POST'])
def update():
    record = json.loads(request.data)
    if record['type']=="SET":
        return change_metrics(record['cluster'], True)
    elif record['type']=="RESET":
        return change_metrics(record['cluster'], False)
    elif record['type']=="SET ALL":
        return change_all_metrics(True)
    elif record['type']=="RESET ALL":
        return change_all_metrics(False)
    else:
        return "Incorrect request type", 400

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Metrics generator")
    parser.add_argument('--conf', dest='conf', help='Config yaml file', default='conf.yaml')
    # Additional config - overrides config.yaml
    parser.add_argument('-n', '--name', dest='name', help='Name of the cluster', default='1')
    args = parser.parse_args()

    opt_config = {
        'name': args.name
    }
    
    create_all_metrics(args.conf, opt_config)
    start_http_server(8000)
    #while(1):
    #    change_all_metrics(True)
    #    time.sleep(2)
    #    change_all_metrics(False)
    #    time.sleep(2)
    app.run(host="0.0.0.0", port=5002, debug=False)
