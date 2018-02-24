# -*- coding: utf-8 -*-
"""Main module.

This module contains code that illustrates ability to extend Locust UI.
It includes:
* new web routes
* a simple test
"""

from locust import HttpLocust, TaskSet, task, web, runners
from locust.runners import MasterLocustRunner
from locust import __version__ as version
from jinja2 import Environment, FileSystemLoader
from flask import request, redirect
from kubernetes import *

DEPLOYMENT = "locust-slave"
NAMESPACE = "default"
HTML_TEMPLATE = 'rescale-form.html'
WORK_DIR = os.path.dirname(__file__)

k8s_service = KubernetesService()


def generate_form():
    j2_env = Environment(loader=FileSystemLoader(WORK_DIR), trim_blocks=True)

    if runners.locust_runner.host:
        host = runners.locust_runner.host
        # TODO try suggestion from pylint: Instead of comparing the length to 0,
        # rely on the fact that empty sequences are false.
    elif len(runners.locust_runner.locust_classes) > 0:
        host = runners.locust_runner.locust_classes[0].host
    else:
        host = None

    is_distributed = isinstance(runners.locust_runner, MasterLocustRunner)
    slave_count = runners.locust_runner.slave_count if is_distributed else 0
    print(f"salve_count: {slave_count}")

    result = j2_env.get_template(HTML_TEMPLATE).render(
        state=runners.locust_runner.state,
        is_distributed=is_distributed,
        user_count=runners.locust_runner.user_count,
        version=version,
        host=host,
        slave_count=slave_count
     )

    return result


@web.app.route("/rescale-form")
def cluster_rescale_form():
    print("entering cluster rescale form")
    return generate_form()


@web.app.route("/rescale", methods=['POST'])
def rescale_action():
    worker_count = request.values.get("worker_count")

    k8s_response = k8s_service.rescale(NAMESPACE, DEPLOYMENT, worker_count)
    # TODO add response code handling

    print(f"rescale response {k8s_response}")
    print(f"response.text: {k8s_response.text}")

    return redirect("/", 302)


class UserTasks(TaskSet):
    @task
    def index(self):
        self.client.get("/")

    @task
    def stats(self):
        self.client.get("/stats/requests")


class WebsiteUser(HttpLocust):
    """
    Locust user class that does requests to the locust web server
    """
    task_set = UserTasks
