As for aggregated results, Locust slaves collect atomic results and combine them to compute aggregations
 (relevant Locust code is located in [stats.py](https://github.com/locustio/locust/blob/0.10.0/locust/stats.py)
  if you are interested) and sent to the master.
You can leverage slave_report event hook to get access to the data. In our case, we have report_data_producer
 method added as the slave_report event listener:
```python
locust.events.slave_report += report_data_producer
```

The listener receives two parameters:
* client_id, which identifies the slave which sent the report
* data, an object with actual payload data

The payload (data) object has the following top level keys: 
```json
{
  "stats":[], "stats_total":{ }, "errors":{}, "user_count":0
}
```




```json
{
  "name":"/get",
  "method":"GET",
  "last_request_timestamp":1558088859,
  "start_time":1558088856.8149574,
  "num_requests":32,
  "num_failures":0,
  "total_response_time":180.03034591674805,
  "max_response_time":7.677793502807617,
  "min_response_time":4.706382751464844,
  "total_content_length":8160,
  "response_times":{
    "6.55055046081543":1,
    ...
    "4.956722259521484":1,
    "5.464076995849609":1
  },
  "num_reqs_per_sec":{
    "1558088856":2,
    "1558088857":9,
    "1558088858":10,
    "1558088859":11
  }
}
```