from queue import Queue


###########
# Exceptions
#
class AdapterError(Exception):
    pass


###########
# Base for concrete adapters
#
class BackendAdapter:

    def id(self):
        return f"{type(self)}"

    def send(self, data):
        pass

    def __hash__(self):
        return hash(self.id())


###########
# Generic forwarder
#
class DBForwarder:
    def __init__(self):
        self.backends = set()
        self.quit = False
        self.forwarder_queue = Queue()

    def add_backend(self, backend_adapter):
        self.backends.add(backend_adapter)
        print(f"backend after addition: {self.backends}")

    def remove_backend(self, backend_adapter):
        self.backends.remove(backend_adapter)
        print(f"backend after removal: {self.backends}")

    def add(self, data):
        """
        Add data to be sent.
        :param data:
        :return:
        """
        print("adding to internal buffer")
        self.forwarder_queue.put(data)

    def run(self):
        print("Started forwarder run loop...")
        # forwarder pops a value and uses a list of adapters to forward it to different sinks
        while not self.quit:
            data = self.forwarder_queue.get()
            for backend in self.backends:
                print(f"db forwarder {backend} sending {data}")
                backend.send(data)
