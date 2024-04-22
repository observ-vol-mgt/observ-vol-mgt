## Local Testing

- Run metricgen, PMF, prometheus, thanos ingestor and query as described in processor readme
- With current release of thanos latest alert manager version supported is v 0.25.0  since later than that use v2 api not supported by thanos yet
- Start alert manager `./alertmanager --config.file=alertmanager.yml`
- Start thanos rule `/thanos rule --grpc-address=0.0.0.0:30901 --query=0.0.0.0:19192 --http-address="0.0.0.0:10903" --rule-file=rules.yml --alertmanagers.url=http://127.0.0.1:9093`
- To test alertmanager receiver start dummy http server `python3 -m http.server 5001`
- To note intevals and wait\_time need to be updated as per notification requirement.
- To dynamically update rules you need to update the file and trigger reload of it in thanos ruler. e.g. using curl: `curl --request POST 0.0.0.0:10903/-/reload` (`http-address` of ruler)
- UI: `0.0.0.0:10903` to view triggered alerts

## APIs for rules
- /add/\<rule\_id\> Add alert rule (if the rule id entry already exists it will replace it)
- /delete/\<rule\_id\> Delete alert rule
- /\<rule\_id\> Get details of an alert rule
- /rules Get details of all the rules

## Example CURLs
- Add rule abc `curl -X POST --data-binary @request.yml -H "Content-type: text/x-yaml" 0.0.0.0:8090/add/abc`
- Delete rule abc `curl  0.0.0.0:8090/delete/abc`
- Get details of rule abc `curl  0.0.0.0:8090/abc`
- Get details of all the rules `curl  0.0.0.0:8090/rules`


