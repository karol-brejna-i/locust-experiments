import time

import zmq


def slave():
    # Connect to the feeder
    context = zmq.Context()
    sock = context.socket(zmq.REQ)
    sock.connect("tcp://localhost:5557")

    while True:
        # Report on duty
        print("announcing I am available")
        sock.send_json({ "msg": "available" })
        print("after announcement")
        # Get the command
        work = sock.recv_json()
        if work == {}:
            print("Nothing else to do!!!")
            continue
        print(f"processing {work}")
        from random import randint
        weight = randint(0, 9)
        time.sleep(weight)


if __name__ == "__main__":
    print("Starting slave")
    slave()