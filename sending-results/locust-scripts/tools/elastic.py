from elasticsearch import Elasticsearch, exceptions

from tools.backend_base import BackendAdapter, AdapterError


class ElasticSearchAdapter(BackendAdapter):
    # https://elasticsearch-py.readthedocs.io/en/master/

    def __init__(self, elastic_hosts=["http://localhost:9200"], index_name="locust", verify_connection=True):
        self.es = Elasticsearch(elastic_hosts)
        self.index_name = index_name
        if verify_connection:
            import datetime
            try:
                print(f"+++++ {datetime.datetime.now()} -- checking the connection")
                print(self.es.cluster.health())
                print(datetime.datetime.now())
            except exceptions.ConnectionError as ce:
                print("connection error")
                raise AdapterError from ce
            except:
                import sys
                print("---------Unexpected error:", sys.exc_info()[0])
                raise AdapterError

    def send(self, data):
        print(f"Sending data {data}")
        # convert data to proper format
        pass

        # store the data in Elasticsearch
        res = self.es.index(index=self.index_name, body=data)
        print(res['result'])


class OtherAdapter(BackendAdapter):
    def __init__(self):
        pass

    def send(self, data):
        pass
