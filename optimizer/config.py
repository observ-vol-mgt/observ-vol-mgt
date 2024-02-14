from typing import List, Tuple
import json
from pprint import pprint
from collections import deque
import bitmath as bm
import numpy as np
import logging.config
import gurobipy as gp
from gurobipy import GRB
from scipy.sparse import rand, coo_matrix
import json

def init_logger(file):
    logger = logging.getLogger(__name__)
    fh = logging.FileHandler(file)
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)
    return logger
    
logger = init_logger('sim.log')

class Anomalies:
    def __init__(self, nMetricsTotal = None, sfreqMask = None, nAnomalyFunctions = None, weightAnomaly = None, anomalyPercentages = None, nMetricsPerAnomaly = None,
                 weightDistAnomaly = None, distParam = None, weightMetricsAnomaly = None, maxTTD = None, weightThreshold = None):
        
        if nAnomalyFunctions == None:
            self.nAnomalyFunctions = 1
            self.weightAnomaly = np.array([1])
        else:
            self.nAnomalyFunctions = nAnomalyFunctions
            if weightAnomaly == None:
                weights = np.random.rand(self.nAnomalyFunctions)
                self.weightAnomaly = weights/sum(weights)
            else:
                self.weightAnomaly = weightAnomaly    

        if nMetricsPerAnomaly == None:
            self.nMetricsPerAnomaly = [nMetricsTotal] * self.nAnomalyFunctions
        elif isinstance(nMetricsPerAnomaly, list):
            self.nMetricsPerAnomaly = nMetricsPerAnomaly
        else:
            self.nMetricsPerAnomaly = [nMetricsPerAnomaly for i in range(self.nAnomalyFunctions)]
        
        logger.info("#Anomaly Functions = " +str(self.nAnomalyFunctions))
        logger.info("Anomaly Weights = " +"".join(str(self.weightAnomaly)))
        logger.info("#Metrics/Anomaly = " +"".join(str(self.nMetricsPerAnomaly)))

        #### Now we need to choose these metrics and assign them weights,
        #### We assume that input is in the form of multiple matrices (precisely, nAnomalyFunctions number of matrices)
        #### Each matrix is of dimension (nEDC * maxPossibleMetricsPerEDC)

        if anomalyPercentages == None:
            self.anomalyPercentages = (1,0,0)
        else:
            self.anomalyPercentages = anomalyPercentages
        logger.info("Anomaly Percentages = " +"".join(str(self.anomalyPercentages)))
        ## TODO: Implement this part.

        if weightDistAnomaly == None:
            self.weightDistAnomaly = 'random'
        else:
            self.weightDistAnomaly = weightDistAnomaly
            self.distParam = distParam
        logger.info("Weight Distibution of Metrics affecting an Anomaly = " +str(self.weightDistAnomaly))
        
        if weightMetricsAnomaly == None:
            self.weightMetricsAnomaly = np.ndarray(shape=(self.nAnomalyFunctions), dtype=coo_matrix) 
            self.generateWeights(sfreqMask)
        else:
            self.weightMetricsAnomaly = weightMetricsAnomaly
        logger.info("Weights of Metrics/Anomaly = " +"".join(str(self.weightMetricsAnomaly)))

        if maxTTD == None:
            self.maxTTD = 1000
        elif isinstance(maxTTD, list):
            self.maxTTD = maxTTD
        else:
            self.maxTTD = [maxTTD for i in range(self.nAnomalyFunctions)]
        logger.info("Max TTD Anomaly = " + "".join(str(self.maxTTD)))  

        if weightThreshold == None:
            self.weightThreshold = 0.8
        else:
            self.weightThreshold = weightThreshold
        logger.info("#Anomaly Functions = " +str(self.weightThreshold))

    def generateWeights(self, sfreqMask):
        nRandomAnomalies = self.anomalyPercentages[0] * self.nAnomalyFunctions 
        for i in range(nRandomAnomalies):
            if self.weightDistAnomaly == 'random':
                randomWeightValues = np.random.rand(self.nMetricsPerAnomaly[i])
            elif self.weightDistAnomaly == 'pareto':
                randomWeightValues = np.random.pareto(self.distParam,self.nMetricsPerAnomaly[i])
            randomWeightValues = randomWeightValues/sum(randomWeightValues)
            self.weightMetricsAnomaly[i] = sfreqMask
            non_zero_indices = np.random.choice(self.weightMetricsAnomaly[i].nonzero()[0].shape[0], size=self.nMetricsPerAnomaly[i], replace=False)
            self.weightMetricsAnomaly[i].data[non_zero_indices] = randomWeightValues

class Baselines:
    def __init__(self, minFrequency = None, maxFrequency = None, staticFrequency = None):
        if minFrequency == None:
            self.minFrequency = 0.001
        else:
            self.minFrequency = minFrequency
        logger.info("Min Frequency = " +str(self.minFrequency))

        if maxFrequency == None:
            self.maxFrequency = 1
        else:
            self.maxFrequency = maxFrequency
        logger.info("MAX Frequency = " +str(self.maxFrequency))

        if staticFrequency == None:
            self.staticFrequency = 1/30
        else:
            self.staticFrequency = staticFrequency
        logger.info("Static Frequency = " +str(self.staticFrequency))



class Config:
    def __init__(self, nRDC = None, nEDC = None, totalBandwidthRDC = None, actBandwidthEDC = None, nClustersPerEDC = None, 
    actClusterMetrics = None, actSizeMetrics = None, anomalies = None, baselines = None):
        if nRDC == None:
            self.nRDC = 1
        else:
            self.nRDC = nRDC
        
        if totalBandwidthRDC == None:
            self.totalBandwidthRDC = bm.kB(4300).to_Byte() 
        else:
            self.totalBandwidthRDC = totalBandwidthRDC

        if nEDC == None:
            self.nEDC = 10
        else:
            self.nEDC = nEDC

        if actBandwidthEDC == None:
            self.actBandwidthEDC = [bm.kB(10000).to_Byte()  for i in range(self.nEDC)]
        else:
            self.actBandwidthEDC = actBandwidthEDC

        if nClustersPerEDC == None:
           self.nClustersPerEDC = [10 for i in range(self.nEDC)]
        elif isinstance(nClustersPerEDC, list):
            self.nClustersPerEDC = nClustersPerEDC
        else:
            self.nClustersPerEDC = [nClustersPerEDC for i in range(self.nEDC)]

        logger.info("#RDCs = " +str(self.nRDC))
        logger.info("BW = " +str(self.totalBandwidthRDC))
        logger.info("#EDCs = " +str(self.nEDC))
        logger.info("BW = " +"".join(str(self.actBandwidthEDC)))
        logger.info("#CLusters/EDC = " +"".join(str(self.nClustersPerEDC)))

        if actClusterMetrics == None:
           self.actClusterMetrics = [[10 for j in range(self.nClustersPerEDC[i])] for i in range(self.nEDC)]
        elif isinstance(actClusterMetrics, list):
            self.actClusterMetrics = actClusterMetrics
        else:
            self.actClusterMetrics = [[actClusterMetrics for j in range(self.nClustersPerEDC[i])] for i in range(self.nEDC)]
        
        self.nMetricsTotal = 0
        nMetricsPerEDC = []
        for i in range(self.nEDC):
            val = 0
            for j in range(self.nClustersPerEDC[i]):
                val += self.actClusterMetrics[i][j]
            nMetricsPerEDC.append(val)
            self.nMetricsTotal += val
        self.maxPossibleMetricsPerEDC = max(nMetricsPerEDC)
        self.maxPossibleClustersPerEDC = max(self.nClustersPerEDC)
        self.maxPossibleMetricsPerCluster = max(max(self.actClusterMetrics))

        self.sfreqMask = self.generateMask()

        if actSizeMetrics == None:
           self.actSizeMetrics =  np.full((self.nEDC, self.maxPossibleMetricsPerEDC), bm.Byte(100))
        elif isinstance(actSizeMetrics, list):
            self.actSizeMetrics = actSizeMetrics
        else:
            self.actSizeMetrics =  np.full((self.nEDC, self.maxPossibleMetricsPerEDC), self.actClusterMetrics)
        self.maxSizeMetrics = bm.Byte(150) 
        

        logger.info("#Metrics/Cluster = " +"".join(str(self.actClusterMetrics)))
        logger.info("#TotalMetrics = " + str(self.nMetricsTotal) + " #MaxMetrics = " + str(self.maxPossibleMetricsPerEDC) + 
                                " #MaxClusters/EDC = " + str(self.maxPossibleClustersPerEDC) + " #MaxMetrics/Cluster = " + str(self.maxPossibleMetricsPerCluster))
        logger.info("Metric Sizes = " +"".join(str(self.actSizeMetrics)))

        self.anomalies = Anomalies(nMetricsTotal = self.nMetricsTotal, sfreqMask = self.sfreqMask, **anomalies)
        self.baselines = Baselines(**baselines)

          
    def generateMask(self):
        freqMask = np.ones((self.nEDC,self.maxPossibleMetricsPerEDC))
        for i in range(self.nEDC):
            for j in range(self.nClustersPerEDC[i]): 
                base = j * self.maxPossibleMetricsPerCluster
                for k in range(self.actClusterMetrics[i][j],self.maxPossibleMetricsPerCluster):
                    freqMask[i][base+k] = 0
            for j in range(self.nClustersPerEDC[i], self.maxPossibleClustersPerEDC):
                base = j * self.maxPossibleMetricsPerCluster
                for j1 in range(self.maxPossibleMetricsPerCluster):
                    freqMask[i][base+j1] = 0
        return coo_matrix(freqMask)


def print_variables(classobj):
    for key, value in vars(classobj).items():
        if isinstance(value, (Anomalies, Baselines)):
            print_variables(value)
        else:
            print(key, ':', value)

def parse_config(data):
    return Config(**data)
