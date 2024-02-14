import json
import config
import code
import logging 
import os
import numpy as np

logging.basicConfig(filename='DFMC.log', encoding='utf-8', level=logging.WARNING)

nRuns = 1
nEDC_set = [10]
nClustersPerEDC_set = [2]
actClusterMetrics_set = [10]
nAnomalyFunctions_set = [1]
weightDistAnomaly_set = ['pareto']
distParam_set = [2]
maxTTD_set = [100]

objWeights_set = [[70, 0.5, 0.6]]  
models = ['model3','model4','model5','model6','baseline','baseline-min', 'baseline-max']
# models = ['model6']
outputfile = 'output_varying_weights.csv'

if not os.path.exists(outputfile):
        print("nEDCs;nClusters/EDC;nMetrics/Cluster;nTotalMetrics;metric-weight-distribution;distribution-param;maxTTD-of-anomaly;model;obj-weights;BW;TTD;PTTD", file=open(outputfile, 'w'))
    

for nEDC in nEDC_set:
    for nClustersPerEDC in nClustersPerEDC_set:
        for actClusterMetrics in actClusterMetrics_set:
            for nAnomalyFunctions in nAnomalyFunctions_set:
                for weightDistAnomaly in weightDistAnomaly_set:
                    for distParam in distParam_set:
                        for maxTTD in maxTTD_set:
                            baselines = {
                                "minFrequency": 10, 
                                "maxFrequency": 1000, 
                                "staticFrequency": 50, 
                            }  
                            anomalies = {
                                "nAnomalyFunctions": nAnomalyFunctions,
                                "weightAnomaly": None,
                                "nMetricsPerAnomaly": None,  
                                "weightDistAnomaly": weightDistAnomaly, 
                                "distParam": distParam,
                                "weightMetricsAnomaly": None,  
                                "maxTTD": maxTTD,
                                "weightThreshold": 0.9,
                                "anomalyPercentages": None
                            }
                            configuration = {
                                "nEDC": nEDC, 
                                "totalBandwidthRDC": None, 
                                "actBandwidthEDC": None, 
                                "nClustersPerEDC": nClustersPerEDC, 
                                "actClusterMetrics": actClusterMetrics, 
                                "actSizeMetrics": None,
                                "anomalies": anomalies,
                                "baselines": baselines
                            }                
                            config_json_str = json.dumps(configuration,indent = 3)
                            configuration = config.parse_config(json.loads(config_json_str))
                            # config.print_variables(configuration)


                            for model in models:
                                print(model)
                                for objWeights in objWeights_set:
                                    result = code.run_model(configuration, model, objWeights)

                                    with open(outputfile,'a') as op:
                                        print(";".join([str(configuration.nEDC), str(configuration.nClustersPerEDC[0]), str(sum(configuration.actClusterMetrics[0])), str(configuration.nMetricsTotal), str(configuration.anomalies.weightDistAnomaly),
                                                    str(configuration.anomalies.distParam), str(configuration.anomalies.maxTTD[0]), str(model), str(objWeights)]), end = ';', file=op)
                                        print(";".join([str(float('%.5g' % x)) for x in result]), file=op)       
                                                                