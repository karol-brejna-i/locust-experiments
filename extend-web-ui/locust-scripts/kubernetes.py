# -*- coding: utf-8 -*-
"""Module kubernetes.

This module allows to communicate with kubernetes API from inside a pod.
"""

import os
import requests


class KubernetesService:
    KUBERNETES_SERVICE_HOST = os.environ.get("KUBERNETES_SERVICE_HOST")
    KUBERNETES_PORT_443_TCP_PORT = os.environ.get("KUBERNETES_PORT_443_TCP_PORT")
    KUBERNETES_URL = f"https://{KUBERNETES_SERVICE_HOST}:{KUBERNETES_PORT_443_TCP_PORT}"
    TOKEN_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/token"

    def __init__(self):
        self.auth_token = self._get_token()
        self.headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json-patch+json',
        }

    @staticmethod
    def _read_from_file(path):
        with open(path) as f:
            read_data = f.read()
        return read_data

    def _get_token(self):
        return self._read_from_file(self.TOKEN_PATH)

    def _get_scale_endpoint(self, namespace, deployment):
        return f"{self.KUBERNETES_URL}/apis/extensions/v1beta1/namespaces/{namespace}/deployments/{deployment}/scale"

    def rescale(self, namespace, deployment, replicas_count: int):
        """
        :param namespace: name of the namespace to work in
        :param deployment: the name of deployment to be rescaled
        :param replicas_count: target number of workers
        :return:
        """
        data = '[{"op":"replace","path":"/spec/replicas","value":' + str(replicas_count) + '}]'
        endpoint = self._get_scale_endpoint(namespace, deployment)
        try:
            result = requests.patch(endpoint, headers=self.headers, data=data, verify=False)
        except Exception as e:
            print(f"Error. {e}")
            result = None

        return result
