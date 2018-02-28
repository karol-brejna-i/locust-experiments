import os

from locust import HttpLocust, TaskSet, task, events, Locust

from additional_handlers import additional_success_handler, additional_failure_handler
from ghost_client import CustomClient

WORK_DIR = os.path.dirname(__file__)

events.request_success += additional_success_handler
events.request_failure += additional_failure_handler


class CustomLocust(Locust):
    """
    This is the abstract Locust class which should be subclassed. It provides an custom client
    that can be used to make requests that will be tracked in Locust's statistics.
    """

    def __init__(self, *args, **kwargs):
        super(CustomLocust, self).__init__(*args, **kwargs)
        self.client = CustomClient("broker", 997)


class CustomUserBehaviour(TaskSet):
    @task
    def task1(self):
        self.client.push("/metrics/")

    @task
    def task2(self):
        self.client.pull("/metrics/")


class WebUserBehaviour(TaskSet):
    @task
    def index(self):
        self.client.get("/")

    @task
    def stats(self):
        self.client.get("/stats/requests")

    @task
    def page404(self):
        self.client.get("/does_not_exist")


class WebUser(HttpLocust):
    """
    Locust user class that does requests to the locust web server
    """
    task_set = WebUserBehaviour


class CustomUser(CustomLocust):
    """
    Locust user class that does requests to the locust web server
    """
    task_set = CustomUserBehaviour
