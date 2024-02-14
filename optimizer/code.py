import bitmath as bm
import numpy as np
import logging
import gurobipy as gp
from gurobipy import GRB
import config



# -----------------------------------------------------------------------------------------------------------------------------------------------------
#                                                   Defining a few utility functions
# -----------------------------------------------------------------------------------------------------------------------------------------------------

def calculate_bandwidth(config_data: config.Config, freqMetricsEdgeCloud_m, is_for_baseline = False):
    totalBWEdgeCloudAll = 0
    totalBWEdgeCloud = []
    for i in range(config_data.nEDC):
        totalBW = 0
        for j in range(config_data.maxPossibleMetricsPerEDC):
            if is_for_baseline:
                frequency = freqMetricsEdgeCloud_m[i][j]
            else:
                frequency = freqMetricsEdgeCloud_m[i][j].x
            totalBW += frequency * config_data.actSizeMetrics[i][j]
        totalBWEdgeCloud.append(totalBW)
        totalBWEdgeCloudAll += totalBWEdgeCloud[i]
    logging.info("Total Bandwidth Allocated = " + str(totalBWEdgeCloudAll))
    return totalBWEdgeCloudAll


def calculate_TTD(config_data: config.Config, freqMetricsEdgeCloud_m):
    ttd = np.ndarray(shape = (config_data.anomalies.nAnomalyFunctions))
    for k in range(config_data.anomalies.nAnomalyFunctions):
        minMetricFreq =config_data.baselines.maxFrequency
        activeMetrics = config_data.anomalies.weightMetricsAnomaly[k].nonzero()
        for i in range(len(activeMetrics[0])):
            freqRetrieved = freqMetricsEdgeCloud_m[activeMetrics[0][i]][activeMetrics[1][i]].X
            if minMetricFreq > freqRetrieved:
                minMetricFreq = freqRetrieved
        ttd[k] =  1/minMetricFreq
    logging.info("TTDs calculated -- " + "".join(str(ttd)))
    return ttd


def calculate_WATTD(config_data: config.Config, freqMetricsEdgeCloud_m, is_for_baseline = False):
    if is_for_baseline:
        return 1/config_data.baselines.staticFrequency
    ttd = calculate_TTD(config_data, freqMetricsEdgeCloud_m)
    wattd = sum(ttd*config_data.anomalies.weightAnomaly)
    logging.info("WATTD calculated -- " + "".join(str(wattd)))
    return wattd


def calculate_PTTD(config_data: config.Config, freqMetricsEdgeCloud_m):  
    pttd = np.ndarray(shape=(config_data.anomalies.nAnomalyFunctions))
    for i in range(config_data.anomalies.nAnomalyFunctions):
        frequencyList = []
        indices = list(zip(config_data.anomalies.weightMetricsAnomaly[i].nonzero()[0],config_data.anomalies.weightMetricsAnomaly[i].nonzero()[1]))
        arrayOfWeights = np.asarray([config_data.anomalies.weightMetricsAnomaly[i].todok()[j,k] for j,k in indices])
        sortedIndices = np.argsort(arrayOfWeights)[::-1]
        sum = 0
        for index in sortedIndices:
            sum += arrayOfWeights[index]
            frequencyList.append(freqMetricsEdgeCloud_m[indices[index][0]][indices[index][1]].x) 
            if sum >= config_data.anomalies.weightThreshold:
                break
        pttd[i] = 1/min(frequencyList)
    logging.info("PTTDs calculated -- " + "".join(str(pttd)))
    return pttd


def calculate_WAPTTD(config_data: config.Config, freqMetricsEdgeCloud_m, is_for_baseline = False):
    if is_for_baseline:
        return 1/config_data.baselines.staticFrequency
    pttd = calculate_PTTD(config_data, freqMetricsEdgeCloud_m)
    wapttd = sum(pttd*config_data.anomalies.weightAnomaly)
    logging.info("WAPTTD calculated -- " + "".join(str(wapttd)))
    return wapttd



# -----------------------------------------------------------------------------------------------------------------------------------------------------
#                                                                  UTILITY FUNCTIONS 
# -----------------------------------------------------------------------------------------------------------------------------------------------------
def handle_zero_frequencies(config_data: config.Config, freqMetricsEdgeCloud_m, m, is_for_baseline):
    if is_for_baseline:
        for i in range(config_data.nEDC):
            for j in range(config_data.nClustersPerEDC[i]):
                base = j * config_data.maxPossibleMetricsPerCluster
                for k in range(config_data.actClusterMetrics[i][j],config_data.maxPossibleMetricsPerCluster):
                    freqMetricsEdgeCloud_m[i][base+k] = 0
            for j in range(config_data.nClustersPerEDC[i], config_data.maxPossibleClustersPerEDC):
                base = j * config_data.maxPossibleMetricsPerCluster
                for j1 in range(config_data.maxPossibleMetricsPerCluster):
                    freqMetricsEdgeCloud_m[i][base+j1] = 0
        return freqMetricsEdgeCloud_m
    else:
        for i in range(config_data.nEDC):
            for j in range(config_data.nClustersPerEDC[i]):
                base = j * config_data.maxPossibleMetricsPerCluster
                for k in range(config_data.actClusterMetrics[i][j]):
                    m.addConstr(freqMetricsEdgeCloud_m[i][base+k] >=config_data.baselines.minFrequency)
                for k in range(config_data.actClusterMetrics[i][j],config_data.maxPossibleMetricsPerCluster):
                    m.addConstr(freqMetricsEdgeCloud_m[i][base+k] == 0)
            for j in range(config_data.nClustersPerEDC[i], config_data.maxPossibleClustersPerEDC):
                base = j * config_data.maxPossibleMetricsPerCluster
                for j1 in range(config_data.maxPossibleMetricsPerCluster):
                    m.addConstr(freqMetricsEdgeCloud_m[i][base+j1] == 0)
        return m

# -----------------------------------------------------------------------------------------------------------------------------------------------------
#                                                                       BASELINES
# -----------------------------------------------------------------------------------------------------------------------------------------------------

def max_frequency(config_data: config.Config):
    logging.info("Max Frequency ----------- ")
    freqMetricsEdgeCloud_m = np.ones(shape = (config_data.nEDC,config_data.maxPossibleMetricsPerEDC)) *config_data.baselines.maxFrequency
    freqMetricsEdgeCloud_m = handle_zero_frequencies(config_data, freqMetricsEdgeCloud_m, 0, True)
    maxFreqBWEdgeCloudAll = calculate_bandwidth(config_data, freqMetricsEdgeCloud_m, True)
    return maxFreqBWEdgeCloudAll, 1/config_data.baselines.maxFrequency, 1/config_data.baselines.maxFrequency
     
def min_frequency(config_data: config.Config):
    logging.info("Min Frequency ----------- ")
    freqMetricsEdgeCloud_m = np.ones(shape = (config_data.nEDC,config_data.maxPossibleMetricsPerEDC)) *config_data.baselines.minFrequency
    freqMetricsEdgeCloud_m = handle_zero_frequencies(config_data, freqMetricsEdgeCloud_m, 0, True)
    minFreqBWEdgeCloudAll = calculate_bandwidth(config_data, freqMetricsEdgeCloud_m, True)
    return minFreqBWEdgeCloudAll, 1/config_data.baselines.minFrequency, 1/config_data.baselines.minFrequency

def static_frequency(config_data: config.Config):
    logging.info("Static Baseline Frequency ----------- ")
    freqMetricsEdgeCloud_m = np.ones(shape = (config_data.nEDC,config_data.maxPossibleMetricsPerEDC)) * config_data.baselines.staticFrequency
    freqMetricsEdgeCloud_m = handle_zero_frequencies(config_data, freqMetricsEdgeCloud_m, 0, True)
    baselineBWEdgeCloudAll = calculate_bandwidth(config_data, freqMetricsEdgeCloud_m, True)
    return baselineBWEdgeCloudAll, calculate_WATTD(config_data, freqMetricsEdgeCloud_m, True), calculate_WAPTTD(config_data, freqMetricsEdgeCloud_m, True)


# -----------------------------------------------------------------------------------------------------------------------------------------------------
#                                                                       MODEL - 3
# -----------------------------------------------------------------------------------------------------------------------------------------------------  
def third_model(config_data: config.Config):
    """
    Model 3: With Anomaly functions - Maximizing sum of weighted frequencies
    """
    logging.info(" ============================= Model 3 ============================= ")

    m = gp.Model('DFMC_multi')

    # Defining optimization variables
    freqMetricsEdgeCloud_m = m.addMVar(shape = (config_data.nEDC, config_data.maxPossibleMetricsPerEDC), vtype = GRB.CONTINUOUS, lb =config_data.baselines.minFrequency, ub =config_data.baselines.maxFrequency)
    
    # Setting a few model parameters
    m.setParam("LogFile",  "Models.log")
    m.setParam(GRB.Param.DualReductions, 0.0)
    m.setParam(GRB.Param.InfUnbdInfo, 1) 

    # Adding constraints
    objSum = 0
    consSum = 0
    totalweightMetricsAnomaly = sum(config_data.anomalies.weightMetricsAnomaly).toarray()
    W = np.array((config_data.maxPossibleMetricsPerEDC,1))
    for i in range(config_data.nEDC):
        W = totalweightMetricsAnomaly[i:i+1, :]
        objSum += W @ freqMetricsEdgeCloud_m[i]
        m.addConstr(config_data.actSizeMetrics[i:i+1, :] @ freqMetricsEdgeCloud_m[i] <= config_data.actBandwidthEDC[i])
        consSum += config_data.actSizeMetrics[i:i+1, :] @ freqMetricsEdgeCloud_m[i] 
    m.addConstr(consSum <= config_data.totalBandwidthRDC)
    m = handle_zero_frequencies(config_data, freqMetricsEdgeCloud_m, m, False)

    # Adding anomaly function constraints
    for i in range(config_data.anomalies.nAnomalyFunctions):
        for j,k in zip(config_data.anomalies.weightMetricsAnomaly[i].nonzero()[0],config_data.anomalies.weightMetricsAnomaly[i].nonzero()[1]):
            m.addConstr(freqMetricsEdgeCloud_m[j][k] >= 1/config_data.anomalies.maxTTD[i]) 

    # Setting objective
    m.setObjective((objSum), GRB.MAXIMIZE)

    # Optimizing model and writing to file
    m.optimize()
    m.printQuality()
    m.write("myModel3.lp")
    
    # Getting optimized values and calculating bandwidth consumption, relWATTD
    totalBWEdgeCloudAll = calculate_bandwidth(config_data, freqMetricsEdgeCloud_m)
    logging.info("Optimal Value of Objective function of Model 3 = " + str(m.objVal))
    logging.info("Max TTD Array: " + str(config_data.anomalies.maxTTD))
    
    wattd = calculate_WATTD(config_data, freqMetricsEdgeCloud_m)
    wapttd = calculate_WAPTTD(config_data, freqMetricsEdgeCloud_m)
    return totalBWEdgeCloudAll, wattd, wapttd 


# -----------------------------------------------------------------------------------------------------------------------------------------------------
#                                                                       MODEL - 4
# -----------------------------------------------------------------------------------------------------------------------------------------------------
def fourth_model(config_data: config.Config, objWeights = [0.33,0.33,0.33]):
    """
    Model 4: With Anomaly functions - Maximizing the minimum frequency for all anomalies
    Done in a process similar to Model 2.
    """
    logging.info(" ============================= Model 4 ============================= ")

    m = gp.Model('DFMC_multiapp')

    # Defining optimization variables
    freqMetricsEdgeCloud_m = m.addMVar(shape = (config_data.nEDC, config_data.maxPossibleMetricsPerEDC), ub =config_data.baselines.maxFrequency)
    lowerbounds = m.addMVar(shape = (config_data.anomalies.nAnomalyFunctions,1), vtype=GRB.CONTINUOUS, ub =config_data.baselines.maxFrequency)

    # Setting a few model parameters
    m.setParam("LogFile",  "Models.log")
    m.setParam(GRB.Param.DualReductions, 0.0)
    m.setParam(GRB.Param.InfUnbdInfo, 1)

    # Adding constraints
    consSum = 0
    for i in range(config_data.nEDC):
        sumOfFrequenciesOfAllMetricsOfEDC = config_data.actSizeMetrics[i:i+1, :] @ freqMetricsEdgeCloud_m[i]
        m.addConstr(sumOfFrequenciesOfAllMetricsOfEDC <= config_data.actBandwidthEDC[i])
        consSum += sumOfFrequenciesOfAllMetricsOfEDC
    m.addConstr(consSum <= config_data.totalBandwidthRDC)
    m = handle_zero_frequencies(config_data, freqMetricsEdgeCloud_m, m, False)

    # Adding anomaly function constraints
    for i in range(config_data.anomalies.nAnomalyFunctions):
        for j,k in zip(config_data.anomalies.weightMetricsAnomaly[i].nonzero()[0],config_data.anomalies.weightMetricsAnomaly[i].nonzero()[1]):
            m.addConstr(lowerbounds[i] <= freqMetricsEdgeCloud_m[j][k]) 
            # m.addConstr(freqMetricsEdgeCloud_m[j][k] >= 1/maxTTD[i]) 
        m.addConstr(lowerbounds[i] >= 1/config_data.anomalies.maxTTD[i])

    # Setting objective - multiple objectives
    m.setAttr("NumObj", config_data.anomalies.nAnomalyFunctions+1)
    m.setAttr("ModelSense", GRB.MAXIMIZE)
    for l in range(config_data.anomalies.nAnomalyFunctions):
        m.setObjectiveN(lowerbounds[l], index = l, weight = objWeights[1]*config_data.anomalies.weightAnomaly[l])
    m.setObjectiveN(consSum, index = config_data.anomalies.nAnomalyFunctions, weight = -1.0 * objWeights[0] / config_data.maxSizeMetrics)
    m.update()
    
    # Optimizing model and writing to file
    m.optimize()
    # m.feasRelaxS(0, False, True, False)
    m.printQuality()
    m.write("myModel4.lp")

    # Getting optimized values and calculating bandwidth consumption, relWATTD, relWAPTTD
    totalBWEdgeCloudAll = calculate_bandwidth(config_data, freqMetricsEdgeCloud_m)    
    logging.info("Optimal Value of Objective function of Model 4 = " + str(m.objVal))
    logging.info("Max TTD Array: " + str(config_data.anomalies.maxTTD))
    
    wattd = calculate_WATTD(config_data, freqMetricsEdgeCloud_m)
    wapttd = calculate_WAPTTD(config_data, freqMetricsEdgeCloud_m)
    logging.info("------------------------------------------------")
    logging.info("BW ==   "+str(objWeights[0]*totalBWEdgeCloudAll/config_data.maxSizeMetrics))
    logging.info("TTD ==  "+str(objWeights[1]*config_data.anomalies.weightAnomaly[l]*wattd))
    logging.info("------------------------------------------------")
    return totalBWEdgeCloudAll, wattd, wapttd 

# -----------------------------------------------------------------------------------------------------------------------------------------------------
#                                                                       MODEL - 5
# -----------------------------------------------------------------------------------------------------------------------------------------------------
def fifth_model(config_data: config.Config, objWeights = [0.33, 0.33, 0.33]):
    """
    Model 5: With Anomaly functions - Maximizing the minimum frequency for K most relevant metrics for each anomaly
    Done in a process similar to Model 2.
    """
    logging.info(" ============================= Model 5 ============================= ")

    m = gp.Model('DFMC_multiapp_K most relevant.lp')

    # Defining optimization variables
    freqMetricsEdgeCloud_m = m.addMVar(shape = (config_data.nEDC, config_data.maxPossibleMetricsPerEDC), ub =config_data.baselines.maxFrequency)
    lowerbounds = m.addMVar(shape = (config_data.anomalies.nAnomalyFunctions,1), vtype=GRB.CONTINUOUS, ub =config_data.baselines.maxFrequency)

    # Setting a few model parameters
    m.setParam(GRB.Param.DualReductions, 0.0)
    m.setParam(GRB.Param.InfUnbdInfo, 1)
    m.setParam("LogFile", "Models.log")
    
    # Adding constraints
    consSum = 0
    for i in range(config_data.nEDC):
        m.addConstr(config_data.actSizeMetrics[i:i+1, :] @ freqMetricsEdgeCloud_m[i] <= config_data.actBandwidthEDC[i])
        consSum += config_data.actSizeMetrics[i:i+1, :] @ freqMetricsEdgeCloud_m[i] 
    m.addConstr(consSum <= config_data.totalBandwidthRDC)
    m = handle_zero_frequencies(config_data, freqMetricsEdgeCloud_m, m, False)

    # Adding anomaly function constraints
    for i in range(config_data.anomalies.nAnomalyFunctions):
        indices = list(zip(config_data.anomalies.weightMetricsAnomaly[i].nonzero()[0],config_data.anomalies.weightMetricsAnomaly[i].nonzero()[1]))
        arrayOfWeights = np.asarray([config_data.anomalies.weightMetricsAnomaly[i].todok()[j,k] for j,k in indices])
        sortedIndices = np.argsort(arrayOfWeights)[::-1]
        sum = 0
        for index in sortedIndices:
            sum += arrayOfWeights[index]
            m.addConstr(lowerbounds[i] <= freqMetricsEdgeCloud_m[indices[index][0]][indices[index][1]])
            if sum >= config_data.anomalies.weightThreshold:
                break
        # m.addConstr(lowerbounds[i] >= 1/maxTTD[i])
        for index in sortedIndices:
            for j,k in indices:
                m.addConstr(freqMetricsEdgeCloud_m[j][k] >= 1/config_data.anomalies.maxTTD[i]) 
    
    # Setting objective - multiple objectives
    m.setAttr("NumObj", config_data.anomalies.nAnomalyFunctions+1)
    m.setAttr("ModelSense", GRB.MAXIMIZE)
    for l in range(config_data.anomalies.nAnomalyFunctions):
        m.setObjectiveN(lowerbounds[l], index = l, weight = objWeights[2]*config_data.anomalies.weightAnomaly[l])
    m.setObjectiveN(consSum, index = config_data.anomalies.nAnomalyFunctions, weight = -1.0* objWeights[0]/config_data.maxSizeMetrics)   # Set the weight this way to normalize 
    m.update()
    
    # Optimizing model and writing to file
    m.optimize()
    # m.feasRelaxS(0, False, True, False)
    m.printQuality()
    m.write("myModel5.lp")

    # Getting optimized values and calculating bandwidth consumption, relWATTD, relWAPTTD
    totalBWEdgeCloudAll = calculate_bandwidth(config_data, freqMetricsEdgeCloud_m)
    logging.info("Optimal Value of Objective function of Model 5 = " + str(m.objVal))
    logging.info("Max TTD Array: " + str(config_data.anomalies.maxTTD))

    wattd = calculate_WATTD(config_data, freqMetricsEdgeCloud_m)
    wapttd = calculate_WAPTTD(config_data, freqMetricsEdgeCloud_m)
    logging.info("------------------------------------------------")
    logging.info("BW ==   "+str(objWeights[0]*totalBWEdgeCloudAll/config_data.maxSizeMetrics))
    logging.info("PTTD == "+str(objWeights[2]*config_data.anomalies.weightAnomaly[l]*wapttd))
    logging.info("------------------------------------------------")
    return totalBWEdgeCloudAll, wattd, wapttd 

# -----------------------------------------------------------------------------------------------------------------------------------------------------
#                                                                       MODEL - 6
# -----------------------------------------------------------------------------------------------------------------------------------------------------
def sixth_model(config_data: config.Config, objWeights = [0.33, 0.33, 0.33]):
    """
    Model 6: With Anomaly functions - TTD, PTTD, Bandwdith in obj
    Done in a process similar to Model 2. Basically combining Models 3, 4 and bandwidth minimization objective.
    """
    logging.info(" ============================= Model 6 ============================= ")

    m = gp.Model('DFMC_multiapp_All_three.lp')

    # Defining optimization variables
    freqMetricsEdgeCloud_m = m.addMVar(shape = (config_data.nEDC, config_data.maxPossibleMetricsPerEDC), ub =config_data.baselines.maxFrequency)
    lowerbounds_ttd = m.addMVar(shape = (config_data.anomalies.nAnomalyFunctions,1), vtype=GRB.CONTINUOUS, ub =config_data.baselines.maxFrequency)
    lowerbounds_pttd = m.addMVar(shape = (config_data.anomalies.nAnomalyFunctions,1), vtype=GRB.CONTINUOUS, ub =config_data.baselines.maxFrequency)

    # Setting a few model parameters
    m.setParam(GRB.Param.DualReductions, 0.0)
    m.setParam(GRB.Param.InfUnbdInfo, 1)
    m.setParam("LogFile", "Models.log")
    
    # Adding constraints
    consSum = 0
    for i in range(config_data.nEDC):
        m.addConstr(config_data.actSizeMetrics[i:i+1, :] @ freqMetricsEdgeCloud_m[i] <= config_data.actBandwidthEDC[i])
        consSum += config_data.actSizeMetrics[i:i+1, :] @ freqMetricsEdgeCloud_m[i] 
    m.addConstr(consSum <= config_data.totalBandwidthRDC)
    m = handle_zero_frequencies(config_data, freqMetricsEdgeCloud_m, m, False)

    # Adding anomaly function constraints
    for i in range(config_data.anomalies.nAnomalyFunctions):
        indices = list(zip(config_data.anomalies.weightMetricsAnomaly[i].nonzero()[0],config_data.anomalies.weightMetricsAnomaly[i].nonzero()[1]))
        arrayOfWeights = np.asarray([config_data.anomalies.weightMetricsAnomaly[i].todok()[j,k] for j,k in indices])
        sortedIndices = np.argsort(arrayOfWeights)[::-1]
        sum = 0
        for index in sortedIndices:
            sum += arrayOfWeights[index]
            m.addConstr(lowerbounds_pttd[i] <= freqMetricsEdgeCloud_m[indices[index][0]][indices[index][1]])
            if sum >= config_data.anomalies.weightThreshold:
                break
        # m.addConstr(lowerbounds[i] >= 1/maxTTD[i])
        for index in sortedIndices:
            for j,k in indices:
                m.addConstr(lowerbounds_ttd[i] <= freqMetricsEdgeCloud_m[j][k]) 
                m.addConstr(freqMetricsEdgeCloud_m[j][k] >= 1/config_data.anomalies.maxTTD[i]) 
        m.addConstr(lowerbounds_ttd[i] >= 1/config_data.anomalies.maxTTD[i])
    
    # Setting objective - multiple objectives
    m.setAttr("NumObj", 2*config_data.anomalies.nAnomalyFunctions+1)
    m.setAttr("ModelSense", GRB.MAXIMIZE)
    for l in range(config_data.anomalies.nAnomalyFunctions):
        m.setObjectiveN(lowerbounds_pttd[l], index = l, weight = objWeights[2]*config_data.anomalies.weightAnomaly[l])
    for l in range(config_data.anomalies.nAnomalyFunctions):
        m.setObjectiveN(lowerbounds_ttd[l], index = config_data.anomalies.nAnomalyFunctions + l, weight = objWeights[1]*config_data.anomalies.weightAnomaly[l])
    m.setObjectiveN(consSum, index = 2*config_data.anomalies.nAnomalyFunctions, weight = -1.0* objWeights[0]/config_data.maxSizeMetrics)   # Set the weight this way to normalize 
    m.update()

    # Optimizing model and writing to file
    m.optimize()
    # m.feasRelaxS(0, False, True, False)
    m.printQuality()
    m.write("myModel6.lp")

    # Getting optimized values and calculating bandwidth consumption, relWATTD, relWAPTTD
    totalBWEdgeCloudAll = calculate_bandwidth(config_data, freqMetricsEdgeCloud_m)
    logging.info("Optimal Value of Objective function of Model 6 = " + str(m.objVal))
    logging.info("Max TTD Array: " + str(config_data.anomalies.maxTTD))

    wattd = calculate_WATTD(config_data, freqMetricsEdgeCloud_m)
    wapttd = calculate_WAPTTD(config_data, freqMetricsEdgeCloud_m)
    logging.info("------------------------------------------------")
    logging.info("BW ==   "+str(objWeights[0]*totalBWEdgeCloudAll/config_data.maxSizeMetrics))
    logging.info("TTD ==  "+str(objWeights[1]*config_data.anomalies.weightAnomaly[l]*wattd))
    logging.info("PTTD == "+str(objWeights[2]*config_data.anomalies.weightAnomaly[l]*wapttd))
    logging.info("------------------------------------------------")
    return totalBWEdgeCloudAll, wattd, wapttd 





# -----------------------------------------------------------------------------------------------------------------------------------------------------
#                                                                       Function to Run
# -----------------------------------------------------------------------------------------------------------------------------------------------------

   
def run_model(configuration, model, objWeights = None):
    result = []
    if model == 'model3':
        result = third_model(configuration)
    elif model == 'model4':
        result = fourth_model(configuration, objWeights)
    elif model == 'model5':
        result = fifth_model(configuration, objWeights)
    elif model == 'model6':
        result = sixth_model(configuration, objWeights)
    elif model == 'baseline':
        result = static_frequency(configuration)
    elif model == 'baseline-min':
        result = min_frequency(configuration)
    elif model == 'baseline-max':
        result = max_frequency(configuration)
    else:
        print("Invalid model!")
    return result

    