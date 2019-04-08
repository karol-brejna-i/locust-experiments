import csv
import os
import queue
import sys
import time

import gevent
import zmq
from locust import TaskSet, task, HttpLocust, events, runners
from locust.runners import MasterLocustRunner, SlaveLocustRunner, LocalLocustRunner

##################
# Reading environment variables and setting up constants
#
FEEDER_HOST = os.getenv("FEEDER_HOST", "127.0.0.1")
FEEDER_BIND_PORT = os.getenv("FEEDER_BIND_PORT", 5555)
FEEDER_ADDR = f"tcp://{FEEDER_HOST}:{FEEDER_BIND_PORT}"
QUIET_MODE = True if os.getenv("QUIET_MODE", "true").lower() in ['1', 'true', 'yes'] else False
TASK_DELAY = int(os.getenv("TASK_DELAY", "1000"))

DATA_SOURCE_PATH = "data.csv"


def log(message):
    if not QUIET_MODE:
        print(message)


##################
# Code related to reading csv files
#
class SourceDataReader:
    """
    Handles reading of source data (csv file) and converting it to desired dict form.
    """

    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        with open(self.file_path, "r") as file:
            reader = csv.DictReader(file)

            data = []
            for element in reader:
                data.append(element)

        return data


##################
# Code related to receiving messages
#
class ZMQRequester:
    def __init__(self, address="tcp://127.0.0.1:5555"):
        """
        :param address: the addres to connect to; defaults to "tcp://127.0.0.1:5555"
        """

        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect(address)
        log("zmq consumer initialized")

    def await_data(self):
        # Inform, that you want some data
        log("announcing I am available")
        self.socket.send_json({"msg": "available"})

        # wait for the data to arrive and return the message
        return self.socket.recv_json()


##################
# Code related to sending messages
#
class ZMQFeeder:
    def __init__(self, data, address="tcp://127.0.0.1:5555"):
        """
        :param data: list of dict objects
        :param address: indicates interface and port to bind to (see: http://api.zeromq.org/2-1:zmq-tcp#toc6);
                        defaults to "tcp://127.0.0.1:5555"
        """
        self.data_queue = queue.Queue()
        [self.data_queue.put(i) for i in data]

        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind(address)
        log("zmq feeder initialized")

    def run(self):
        log("start sending...")
        while True:
            log("before receive")
            j = self.socket.recv_json()
            log("after receive")
            if j["msg"] == "available":
                try:
                    work = self.data_queue.get(block=False)
                    self.socket.send_json(work)
                    self.data_queue.task_done()
                except queue.Empty:
                    # We need to reply something, still...
                    log("Queue empty. We need to reply something...")
                    self.socket.send_json({})
            # yield
            time.sleep(0)


def init_feeder():
    sender = ZMQFeeder(INPUT_DATA, f"tcp://0.0.0.0:{FEEDER_BIND_PORT}")
    sender.run()


##################
# Code for detecting run context
#
def is_test_ran_on_master(): return isinstance(runners.locust_runner, MasterLocustRunner)
def is_test_ran_on_slave(): return isinstance(runners.locust_runner, SlaveLocustRunner)
def is_test_ran_on_standalone(): return isinstance(runners.locust_runner, LocalLocustRunner)
def is_locustfile_ran_on_master(): return '--master' in sys.argv
def is_locustfile_ran_on_slave(): return '--slave' in sys.argv
def is_locustfile_ran_on_standalone(): return not ('--slave' in sys.argv or '--master' in sys.argv)


##################
# Code to be run before the tests
#
def on_master_start_hatching():
    log("on_master_start_hatching")
    # start sending the messages (in a separate greenlet, so it doesn't block)
    gevent.spawn(init_feeder)


events.master_start_hatching += on_master_start_hatching

##################
# Code to be run exactly once, at node startup
#
if is_locustfile_ran_on_master() or is_locustfile_ran_on_standalone():
    log("Reading input data...")
    sdr = SourceDataReader(DATA_SOURCE_PATH)
    INPUT_DATA = sdr.read()
    log(f"{len(INPUT_DATA)} records read")


class TestBehaviour(TaskSet):
    def on_start(self):
        self.zmq_consumer = ZMQRequester(FEEDER_ADDR)

    @task
    def task1(self):
        log("task1")
        # self.__logic__()
        gevent.spawn(self.__logic__)

    def __logic__(self):
        data = self.zmq_consumer.await_data()
        if data == {}:
            log("Nothing else to do!!!")
        else:
            log(f"using the following data to make a request {data}")
            # XXX TODO debugging stuff:
            mark("received", data)

            self.client.post("/post", json=data)


class TestUser(HttpLocust):
    """
    Locust user class that uses external data to feed the locust
    """
    task_set = TestBehaviour
    min_wait = TASK_DELAY
    max_wait = TASK_DELAY


##
def mark(category, message):
    import datetime
    now = datetime.datetime.now()

    new_path = f"./{category}.txt"
    with open(new_path, 'a') as file:
        file.write(f"{now}\t{message}\n")
