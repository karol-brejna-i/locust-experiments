import time

import zmq

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.connect("tcp://127.0.0.1:5555")

delay = 1

while True:
    message = socket.recv()
    print(f"recv: {message}")
    time.sleep(delay)
