import csv
import os
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
class ZMQPoller:
    def __init__(self, address="tcp://127.0.0.1:5555", polling_interval=100):
        """
        :param address: defaults to "tcp://127.0.0.1:5555"
        :param polling_interval: timeout for polling the message; defaults to 100 ms
        """

        self.polling_interval = polling_interval

        context = zmq.Context()
        self.socket = context.socket(zmq.PULL)
        self.socket.connect(address)
        log("zmq consumer initialized")

    def await_data(self):
        log("on read")
        evnts = self.socket.poll(self.polling_interval)

        if evnts:
            message = self.socket.recv_json()
            # log(f"recv: {message}")
            return message
        else:
            log("still waiting")
            return None


##################
# Code related to sending messages
#
class ZMQSender:
    def __init__(self, data, address="tcp://127.0.0.1:5555"):
        """

        :param address: defaults to "tcp://127.0.0.1:5555"
        """

        self.data = data

        context = zmq.Context()
        self.socket = context.socket(zmq.PUSH)
        # bind to all interfaces (http://api.zeromq.org/2-1:zmq-tcp#toc6)
        self.socket.bind(address)
        log("zmq sender initialized")

    def run(self):
        log("start sending...")
        for bit in self.data:
            log(f"sending {bit}")
            self.socket.send_json(bit)
            time.sleep(0)


def init_feeder():
    sender = ZMQSender(INPUT_DATA, f"tcp://0.0.0.0:{FEEDER_BIND_PORT}")
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
        self.zmq_consumer = ZMQPoller(FEEDER_ADDR)

    def __logic__(self):
        data = self.zmq_consumer.await_data()
        if data:
            log(f"using the following data to make a request {data}")
            # XXX TODO debugging stuff:
            mark("received", data)

            self.client.post("http://example.com", json=data)

    @task
    def task1(self):
        log("task1")
        self.__logic__()


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
