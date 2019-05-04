
One of the things that Locust does for you when used as your testing tool is collecting request/response data. 

By default Locust periodically dumps test results and computed aggregated values like median, average response time, number of requests per second, etc.

They are presented in the UI, printed in the logs or can be persisted to a file (using - csv option).

Basically, you have access to request-specific distribution pre-aggregated data.

Most of the time, information presented in such a way is good enough. 

In this article, I'll try to show how to deal with cases where you would like to do more with the results - correlating with some CPU/mem/IO metrics, archiving for future analysis, drawing charts, etc.  - which would require storing them in a database. 

Moreover, let's assume that having only aggregated data is not enough (for example you want to be able to analyze/drill the results down to a single request).

In one of the previous installments of this series, Locust.io experiments  - enriching results (https://medium.com/locust-io-experiments/locust-io-experiments-enriching-results-183d2ae4a4c2), I've touched on the topic of capturing atomic results. 
Now, building upon the information on how to access individual requests data, I will introduce the following elements:
* accessing aggregated request data in a programmatic way,
* sending data to an external database,
* making sure that the communication doesn't affect test performance.

See https://medium.com/p/bd3de1994259 for detailed explaination of the code

## Project contents
[This project](../sending-results) contains:
  * Python source code ([locust-scripts](./locust-scripts)):
    * for collecting the results (pre-aggregated and individual)
    * for sending the results to Elasticsearch
    * with example test that is producing some results
  * Dockerfile for an image containing Locust with all required dependencies installed (`elasticsearch` library)
  * bunch of docker-compose files for setting up the experiment:
    * docker-compose-elastic.yml - for Elasticsearch and Kibana
    * docker-compose-mini.yml - minimal (one node) Elasticsearch "cluster" and Kibana
    * docker-compose.yml - for locust cluster and system under test


## Building the image
```
docker build -t grubykarol/sending-experiment .
```

## Running the experiment
Starting Elasticsearch and Kibana:

```bash
docker-compose -f docker-compose-mini.yml up -d
```

Elasticsearch will be started in a single-node "development" mode (to simplify things).
If you want to have everything "clean" there, you should update the default replication factor for the indices:

```bash
curl -H "Content-Type: application/json" -XPUT "http://localhost:9200/_template/dev" -d '
{
  "order": 0,
  "index_patterns": "locust*",
  "settings": {
    "number_of_replicas": 0
  },
  "mappings": {
      "numeric_detection": true,
      "dynamic_templates": [
        {
          "time_as_double": {
            "path_match" : "payload.*_time",
            "mapping": {
              "type": "double"
            }
          }
        }
      ]
    }
}'
```

Starting locust:
```bash
docker-compose -f docker-compose-headless.yml up
```
or
```bash
docker-compose -f docker-compose-headless.yml up httpbin sut master slave
```