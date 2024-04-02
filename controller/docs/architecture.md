# Volume Manager Controller
## Architecture

The volume manager controller receives information from observability collectors and observability processors. It performs a set of operations to contextualize and analyze the information, and in conjunction with user-provided policies, generates insights and conducts automation operations to control and optimize the volume of observability data.
The volume manager is architectured around pipelines of tasks that are executed asynchronously. Each task performs a different functionality and the pipelines are configurable to allow flexibility and support for various use cases.
The tasks are parallelized and optimized to provide scalability and efficiency. Tasks are typed. Each type has a different characteristic and functionality. Each task operates on a different data structure and emits a different data structure. The controller organizes instances of the tasks in DAGs and operates on them periodically and on-demand as data is ingested into the controller and batched between the various operations performed by the tasks.
The controller also requires data persistency to operate against data structures and efficiently analyze observability data over time. Data persistency is decoupled from the computing tasks allowing flexibility of implementation for specific use cases. 
The behavior of the controller is managed by a set of user-facing high-level semantic policies This allows the controller to be intent-based managed. The controller analyzes the policies and intersects them with the observed data to generate insights and configurations to manage the volume of observability data.

Following are the task types, and a brief explanation of the functionality of each type:

- Ingest  Ingest tasks are responsible for ingesting information into the controller.  The main set of objects ingested into the controller is “signals”. Signals are based on common observability data sources: metrics, logs, traces, etc. Signals can be ingested into the controller synchronously or asynchronously. 

- Grouping  Grouping tasks use information from the signals to cluster, group, and partition several signals into a signal group. The grouping rules are policy-driven and rely on meta-data and data from the signals. The categorization is typically based on labels provided as part of the signals. 

- Feature-Extraction  Feature Extraction tasks are responsible for the basic statistical analysis of the signals. They analyze the signal behaviors and produce a basic set of understandings of the signals. 

- Observability-Analysis  Observability analysis tasks are responsible for domain-specific analysis of signals generating observability-level understandings of signals 

- User-Policy-Analyzer  The policy enforcer will intersect the user-provided policies with the observability signals information and analysis gathered by the controller to generate policy driver information.

- System-Policy-Analyzer  system policy analyzer tasks are responsible for the analysis of system behavior and the correlation of system risk analysis with the observability data. The  tasks will annotate the signals with relevant information to identify the dynamic applicability of the signals according to the policies
Signal-Insight  Insight tasks are responsible for the generation of volume management insights. Those insights are user-facing outputs of the pipelines and according to policies can be consumed by the users or pushed. The insights are tangible, environment-specific, and dynamic. They provide insights into volume management behaviors and action recommendations.
Automation/configuration generator  Automation tasks are responsible for the generation of per-processor configuration based on the action recommendation of the insights tasks. The configurations are sent using a customer-provided control plane to the processors to enforce the volume management reductions automatically.

For common use cases, the volume manager controller pipeline can be as follows:



 
TBD:

Configurations  the configuration tasks are 

Feature extraction  feature 

Persistency:

Objects to consider:


