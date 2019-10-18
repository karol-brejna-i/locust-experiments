import sys

from locust import runners
from locust.runners import MasterLocustRunner, SlaveLocustRunner, LocalLocustRunner


def is_test_ran_on_master(): return isinstance(runners.locust_runner, MasterLocustRunner)


def is_test_ran_on_slave(): return isinstance(runners.locust_runner, SlaveLocustRunner)


def is_test_ran_on_standalone(): return isinstance(runners.locust_runner, LocalLocustRunner)


def is_locustfile_ran_on_master(): return '--master' in sys.argv


def is_locustfile_ran_on_slave(): return '--slave' in sys.argv


def is_locustfile_ran_on_standalone(): return not ('--slave' in sys.argv or '--master' in sys.argv)
