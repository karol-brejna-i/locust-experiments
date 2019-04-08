# PUSH - PULL

Simplified example of PUSH-PULL communication using 0mq.

Run one pusher:
```
python pusher.py
```

Run many pullers:
```
python puller.py
```
or
```
python non-blocking-puller.py
```



## Some background

Initially I was surprised that `send_string` blocked until a message could be read.
(I thought it will be stored in some internal buffer, etc.)

The docs explain it is intentional (http://api.zeromq.org/2-1:zmq-socket#toc12):

    ZMQ_PUSH
    A socket of type ZMQ_PUSH is used by a pipeline node to send messages to downstream pipeline nodes. Messages are round-robined to all connected downstream nodes. The zmq_recv() function is not implemented for this socket type.

    When a ZMQ_PUSH socket enters an exceptional state due to having reached the high water mark for all downstream nodes,
    or _if there are no downstream nodes_ at all, then any zmq_send(3) _operations on the socket shall block_ until the exceptional state ends
    or at least one downstream node becomes available for sending; messages are not discarded.

I chose to accept it. It doesn't harm the flow of the test: as soon the users (locusts) come to life, they will pop the message from the sender.
Also, I decided to use this as an excuse to introduce another locust technique - waiting for all the locusts to hatch.
(execution blocks until all the clients are created.)