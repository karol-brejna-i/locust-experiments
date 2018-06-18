import os
import queue

import zmq

NO_OF_MESSAGES = int(os.getenv("NO_OF_MESSAGES", "100"))

# Prepare dataset
input_data = range(NO_OF_MESSAGES)
data_queue = queue.Queue()
[data_queue.put({"message": "do some work", "payload": i}) for i in input_data]


def master():
    # Setup 0mq connection for the feeder
    context = zmq.Context()
    sock = context.socket(zmq.REP)
    sock.bind("tcp://0.0.0.0:5557")

    items_sent = 0
    while True:
        print("waiting for a client")
        j = sock.recv_json()

        if j['msg'] == "available":
            try:
                work = data_queue.get(block=False)
                print(f"Sending message {work}")
                sock.send_json(work)
                data_queue.task_done()
                items_sent = items_sent + 1
            except queue.Empty:
                # We need to reply something...
                print(f"Sending 'nothing to do'")
                sock.send_json({})


if __name__ == "__main__":
    print("A kuku")
    master()
