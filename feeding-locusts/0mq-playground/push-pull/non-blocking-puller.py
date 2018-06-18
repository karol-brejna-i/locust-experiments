import zmq

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.connect("tcp://127.0.0.1:5555")

while True:
    message = socket.poll(100)

    if message:
        print(f"poller: {message}")
        message = socket.recv()
        print(f"recv: {message}")
    else:
        print("still waiting")
