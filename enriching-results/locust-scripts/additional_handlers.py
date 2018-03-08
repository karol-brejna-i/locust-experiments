""" additional Locust handlers """
import json

OK_TEMPLATE = '{"request_type":"%s", "name":"%s", "result":"%s", ' \
              '"response_time":"%s", "response_length":"%s", "other":%s}'

ERR_TEMPLATE = '{"request_type":"%s", "name":"%s", "result":"%s", ' \
               '"response_time":"%s", "exception":"%s", "other":%s}'


def additional_success_handler(request_type, name, response_time, response_length, **kwargs):
    """ additional request success handler to log statistics """
    print(OK_TEMPLATE % (request_type, name, "OK", response_time, response_length, json.dumps(kwargs)))


def additional_failure_handler(request_type, name, response_time, exception, **kwargs):
    """ additional request failure handler to log statistics """
    print(ERR_TEMPLATE % (request_type, name, "ERR", response_time, exception,  json.dumps(kwargs)))
