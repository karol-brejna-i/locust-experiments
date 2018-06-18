import time

import zmq

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.bind("tcp://127.0.0.1:5555")

delay = 1

i = 0

while True:
    print(f"sending {i}")
    socket.send_string(f"message {i}")
    i += 1
    if i == 100:
        break
    time.sleep(delay)
