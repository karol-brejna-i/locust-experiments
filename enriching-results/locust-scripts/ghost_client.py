""" custom client """

import inspect
import random
import time

from locust import events


def custom_timer(func):
    """ measure time and send to Locust """

    def func_wrapper(*args, **kwargs):
        """ wrap functions and measure time """

        previous_frame = inspect.currentframe().f_back
        (filename, line_number, function_name, lines, index) = inspect.getframeinfo(previous_frame)

        topic = args[1]
        request_name = f"{func.__name__} {topic}"
        start_time = time.time()
        result = None
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type="CUSTOM", name=request_name,
                                        response_time=total_time, exception=e, tag=function_name)
        else:
            total_time = int((time.time() - start_time) * 1000)
            events.request_success.fire(request_type="CUSTOM", name=request_name,
                                        response_time=total_time, response_length=0, tag=function_name)
        return result

    return func_wrapper


class CustomClient:
    """
    Fake custom client.
    Provides two operations that actually only sleep (random time) and occasionally fail.
    """
    __MAX_TIME = 100  # max sleep time [ms]
    __FAILURE_PROBABILITY = 0.05

    def __init__(self, host, port):
        """ Initialize the connection """
        print(f"Connection to {host}:{port} initialized.")

    def _sleep(self):
        time.sleep(random.randint(0, self.__MAX_TIME) / 1000)

    def _decide_the_fate(self):
        if random.random() < self.__FAILURE_PROBABILITY:
            raise Exception("Communication error!")

    @custom_timer
    def push(self, topic):
        """ push message using custom protocol """
        print(f"Making a virtual data push to {topic}")
        # simulate execution time
        self._sleep()
        # simulate success/failure
        self._decide_the_fate()

    @custom_timer
    def pull(self, topic):
        """ pull message using custom protocol """
        print(f"Making a virtual data pull from {topic}")
        # simulate execution time
        self._sleep()
        # simulate success/failure
        self._decide_the_fate()
