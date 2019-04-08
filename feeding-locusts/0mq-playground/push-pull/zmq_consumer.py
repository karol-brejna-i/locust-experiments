import time

import zmq


class ZMQConsumer:
    def __init__(self, on_message, address="tcp://127.0.0.1:5555", polling_interval=100):
        """

        :param on_message: method to be invoked when a message is received
        :param address: defaults to "tcp://127.0.0.1:5555"
        :param polling_interval timeout for polling the message; defaults to 100 ms
        """

        self.polling_interval = polling_interval
        self.on_message_handler = on_message

        context = zmq.Context()
        self.socket = context.socket(zmq.PULL)
        self.socket.connect(address)

    def run(self):
        while True:
            evnts = self.socket.poll(self.polling_interval)

            if evnts:
                message = self.socket.recv()
                self.on_message_handler(message)
            else:
                print("still waiting")
                time.sleep(0)


def my_handler(message):
    print(f"I received {message}.")


if __name__ == '__main__':
    consumer = ZMQConsumer(my_handler)
    print("Consumer initialized. Waiting for messages.")
    consumer.run()