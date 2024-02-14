# Details of Simulation Code (code.py)

## Packages Used: 

    Numpy, SciPy, Gurobipy, Bitmath
    To set Gurobi license, use this --- export GRB_LICENSE_FILE=/Users/aishwariya/Downloads/gurobi.lic

<br/>

## How to Run the Code:

<br/>

### Step 1. Install Requirements
>pip3 install -r requirements.txt
(you need to have Python3 and pip3 installed)

<br/>

### Step 2. Run the code 
>python3 -i code.py

<br/>

### Step 3. Run all models and baseline
> run_all()

### OR

### Step 3. To run any particular model or subset of models
> initialize_system()
##### Model 1
> first_model()
##### Model 2
> second_model()
##### Model 3
> third_model()
##### Model 4
> fourth_model()
##### Model 5
> fifth_model()
##### Model 6
> sixth_model()
#### Baselines
> baseline()

<br/><br/>

### How to Check Output:
<br/>

    1. Open the file 'DFMC.log' created in the code folder.
    - This file contains the details of the system initiliased and the output of the baselines and all the models, e.g., Bandwidth, TTD, PTTD. 
  
    2. Open the file 'ModelX.log' created in the code folder.
    - This file contains the details of the optimization process of ModelX.
  
<br/><br/>

### Functions Used and Their Descriptions
<br/>

| Function Name | Description |
| ----------- | ----------- |
| `initialize_system` | Defines the edge-cloud system, its various components and metrics and the different anomaly functions |
| `calculate_bandwidth` | Calculates the total allocated bandwdith for a given frequency matrix |
| `calculate_TTD` | Calculates the TTD for a given frequency matrix |
| `calculate_WATTD` | Calculates the WATTD for a given frequency matrix |
| `calculate_relWATTD` | Calculates the relWATTD for a given frequency matrix |
| `calculate_PTTD` | Calculates the PTTD for a given frequency matrix |
| `calculate_WAPTTD` | Calculates the WAPTTD for a given frequency matrix |
| `calculate_relWAPTTD` | Calculates the relWAPTTD for a given frequency matrix |
| `handle_zero_frequencies` | Sets the frequencies of unused metrics as zero |
| `max_frequency` | Calculates the total bandwidth requirement when all metrics set to maximum monitoring frequency |
| `min_frequency` | Calculates the total bandwidth requirement when all metrics set to minimum monitoring frequency |
| `static_frequency` | Calculates the total bandwidth requirement when all metrics set to a fixed monitoring frequency |
| `baseline` | Runs all baselines |
| `first_model` | Implements Model 1 |
| `second_model` | Implements Model 2 |
| `third_model` | Implements Model 3 |
| `fourth_model` | Implements Model 4 |
| `fifth_model` | Implements Model 5 |
| `sixth_model` | Implements Model 6 |
| `run_all` | Executes all functions |

<br/><br/>

# Details of Results

This folder constains the data files and plot files generated from the simulation of Static Frequency baseline and Model 6. There are two plots:

1. Frequency Histogram of Metrics - Number of metrics with freequency in a given range of values 

    ![](Results/frequencyplot.png) 

2. TTD/PTTD vs Bandwidth - TTD and PTTD using Model 6 and Static Frequency baseline for the same bandwidth consumption, varied over a given range of bandwidth
   
    ![](Results/timeplot.png) 




