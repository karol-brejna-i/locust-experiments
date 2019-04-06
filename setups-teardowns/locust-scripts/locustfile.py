import os

from gevent.lock import Semaphore
from locust import TaskSet, task, HttpLocust, events, runners
from locust.runners import MasterLocustRunner, SlaveLocustRunner, LocalLocustRunner

TASK_DELAY = int(os.getenv("TASK_DELAY", "1000"))


# Helper function to make the code a little more concise
def show_hook_info():
    import inspect
    caller = inspect.stack()[1][3]
    print(f" --- {caller} executed on {type(runners.locust_runner)}")


##################
# Code for detecting run context
#
def is_test_ran_on_master(): return isinstance(runners.locust_runner, MasterLocustRunner)
def is_test_ran_on_slave(): return isinstance(runners.locust_runner, SlaveLocustRunner)
def is_test_ran_on_standalone(): return isinstance(runners.locust_runner, LocalLocustRunner)


# Should run when:
#   * on Slave: when all required locust had hatched (required number of users is created)
#   * on Master: when all slaves reported hatch complete
#   * on Standalone: when all required locust had hatched (required number of users is created)
def on_hatch_complete(**kwargs):
    show_hook_info()
    is_master = is_test_ran_on_master()
    is_slave = is_test_ran_on_slave()
    is_standalone = is_test_ran_on_standalone()

    if is_slave or is_standalone:
        # unblock the locusts
        all_locusts_spawned.release()


# Should run on master when the tests are started ("start swarming" button on GUI pressed,
# or locust cluster started with --no-web switch)
def on_master_start_hatching():
    show_hook_info()


# Should run on a slave or standalone node when the tests are started ("start swarming" button on GUI pressed,
# or locust cluster started with --no-web switch)
def on_locust_start_hatching():
    show_hook_info()


events.hatch_complete += on_hatch_complete
events.locust_start_hatching += on_locust_start_hatching
events.master_start_hatching += on_master_start_hatching

# This will be executed once, at the node start time
print("Running some code at node start time.")

all_locusts_spawned = Semaphore()
all_locusts_spawned.acquire()


class TestBehaviour(TaskSet):
    # https://docs.locust.io/en/stable/writing-a-locustfile.html#the-on-start-and-on-stop-methods
    def on_start(self):
        print(f"on_start {id(self)}")

        print("waiting for all locusts to spawn...")
        all_locusts_spawned.wait()
        print("continue execution!")

    def on_stop(self):
        print(f"on_stop {id(self)}")

    # https://docs.locust.io/en/stable/writing-a-locustfile.html#setups-and-teardowns
    def setup(self):
        print(f"------- TASKSET setup {id(self)}")

    def teardown(self):
        print(f"------- TASKSET teardown {id(self)}")

    @task
    def task1(self):
        print("task1")


class TestUser(HttpLocust):
    def setup(self):
        print(f"------- LOCUST setup {id(self)}")

    def teardown(self):
        print(f"-------- LOCUST teardown {id(self)}")

    task_set = TestBehaviour
    min_wait = TASK_DELAY
    max_wait = TASK_DELAY
