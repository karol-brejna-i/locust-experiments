import json
import os
from random import randint

import gevent
import locust
from locust import TaskSet, task, HttpLocust, events

from tools.backend_base import DBForwarder
from tools.detectors import *
from tools.elastic import ElasticSearchAdapter

##################
# Reading environment variables and setting up constants
#
ES_CONNECTIONS = os.getenv("ES_CONNECTIONS", "127.0.0.1:9200").split(sep=",")
QUIET_MODE = True if os.getenv("QUIET_MODE", "true").lower() in ['1', 'true', 'yes'] else False
TASK_DELAY = int(os.getenv("TASK_DELAY", "1000"))


def log(message):
    if not QUIET_MODE:
        print(message)


###
#
# configuration for the master
if is_locustfile_ran_on_master() or is_locustfile_ran_on_standalone():
    def report_data_producer(client_id, data):
        print(f"-------------------------data_producer({client_id}, {data})")

        # dissect the report
        # the slave report data format is: # 'stats':[], 'stats_total':{  }, errors':{}, 'user_count':0
        # for this example, let's only take _stats_ (iterate over the array elements
        # and produce individual records for each of them) and _total_ fields
        global forwarder
        total_stat = {"type": "total", "source": client_id, "payload": data["stats_total"]}
        forwarder.add(total_stat)

        for stat in data["stats"]:
            print(f"stat: {stat}")
            aggregated_stat_message = {"type": "aggregated", "source": client_id, "payload": stat}
            forwarder.add(aggregated_stat_message)


    print("starting external db forwarder on master")
    forwarder = DBForwarder()

    ea = ElasticSearchAdapter(ES_CONNECTIONS)
    forwarder.add_backend(ea)
    gevent.spawn(forwarder.run)

    print("adding slave_report hook")
    locust.events.slave_report += report_data_producer

###
#
# configuration for the slave
if is_locustfile_ran_on_slave() or is_test_ran_on_standalone():
    print("starting external db forwarder on slave")
    forwarder = DBForwarder()

    ea = ElasticSearchAdapter(ES_CONNECTIONS)
    forwarder.add_backend(ea)
    gevent.spawn(forwarder.run)


    def additional_success_handler(request_type, name, response_time, response_length, **kwargs):
        """ additional request success handler to log statistics """
        OK_TEMPLATE = '{"request_type":"%s", "name":"%s", "result":"%s", ' \
                      '"response_time":%s, "response_length":%s, "other":%s}'

        json_string = OK_TEMPLATE % (request_type, name, "OK", response_time, response_length, json.dumps(kwargs))
        message = {"type": "success", "payload": json.loads(json_string)}
        forwarder.add(message)


    def additional_failure_handler(request_type, name, response_time, exception, **kwargs):
        """ additional request failure handler to log statistics """
        ERR_TEMPLATE = '{"request_type":"%s", "name":"%s", "result":"%s", ' \
                       '"response_time":%s, "exception":"%s", "other":%s}'
        json_string = ERR_TEMPLATE % (request_type, name, "ERR", response_time, exception, json.dumps(kwargs))
        message = {"type": "error", "payload": json.loads(json_string)}
        forwarder.add(message)


    events.request_success += additional_success_handler
    events.request_failure += additional_failure_handler


class TestBehaviour(TaskSet):
    @task
    def task1(self):
        gevent.spawn(self.client.put, f"/delay/{randint(0, 9)}", name="/delayed")

    @task
    def task2(self):
        self.client.get("/get")

    @task
    def task3(self):
        self.client.post("/post", json={"one": "two"})

    @task
    def task4(self):
        self.client.get("/status/404")


class TestUser(HttpLocust):
    task_set = TestBehaviour
    min_wait = TASK_DELAY
    max_wait = TASK_DELAY
