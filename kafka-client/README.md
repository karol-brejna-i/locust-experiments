Last time I created a custom client for Locust. I think it will be beneficial to continue with the topic.

Firstly, the client was a mock — all it did was to emulate requests/responses for some artificial system.
Secondly, it worked in a synchronous manner: the requests code blocked until the response arrived. This is exactly how the default HTTP client works.

The next step would be to verify how to test systems that provide some kind of non-blocking API and to create a REAL client.

Apache Kafka is quite a popular piece of software that allows for exchange of data/messages between systems
(an up-to-date slogan now seems to be: [open-source stream processing software platform](https://en.wikipedia.org/w/index.php?title=Apache_Kafka&oldid=830231292).
As you probably already know (or will discover soon, if trying to find out more) it has many uses, including some “serious” applications.
It is very performant: it is supposed to handle millions messages per second on commodity hardware.
It also happens that Kafka producer (a component that is responsible for sending messages to Kafka) provides
non-blocking API by default (see: https://kafka.apache.org/10/javadoc/index.html?org/apache/kafka/clients/producer/KafkaProducer.html).

So, creating a Kafka client for Locust could be a time well invested!

There is an accompanying article describing the process and results of creating a Kafka client here: https://medium.com/locust-io-experiments/locust-experiments-locust-meets-kafka-b9d9e6e49537.
Please, take a look at it. 

Below you'll find some additional technical details that can help with understanding and reproducing the experiment.

# Development environment setup

In order to be able to develop the Kafka client and test it, I need an environment with a working Kafka cluster and Locust cluster.

You can achieve it in many ways:
* connect to an existing Kafka cluster,
* have "bare metal" Kafka deployment  - in *nix world it’s quite easy
* use docker  -  there are many docker images that allow for running Kafka in Docker (https://github.com/wurstmeister/kafka-docker being one of the most popular),
* Kubernetes  - this is the option I opted for. First of all, I have already tested Locust cluster creation with K8s.

For me, personally, the easiest approach is to go with K8s. It manages the containers, helps mak networking right, etc.

Please, take a look at [kuberenetes](kubernetes) folder for the details on how to set up Locust and Kafka in Kubernetes for this experiment.

# The code

[locust-scripts](locust-scripts) folder holds the sources:
* [locustfile.py](locust-scripts/locustfile.py) - example test using Kafka client (sends random strings to given topics)
* [additional_handlers.py](locust-scripts/additional_handlers.py) - additional request success/failure handlers for debug purposes (when turned on, they will log every single Kafka request to STDOUT)
* [kafka_client.py](locust-scripts/kafka_client.py) - Kafka client code

See https://medium.com/locust-io-experiments/locust-experiments-locust-meets-kafka-b9d9e6e49537 for a detailed description.