Last time I created a custom client for Locust. I think it will be beneficial to continue with the topic. 

Firstly, the client was a mock — all it did was to emulate requests/responses for some artificial system. 
Secondly, it worked in a synchronous manner: the requests code blocked until the response arrived. This is exactly how the default HTTP client works.

The next step would be to verify how to test systems that provide some kind of non-blocking API and to create a REAL client.

Apache Kafka is quite a popular piece of software that allows for an exchange of data/messages between systems
(an up-to-date slogan now seems to be: open-source stream processing software platform). 
As you probably already know (or will discover soon, if trying to find out more) it has many uses,
including some “serious” applications. It is very performant: it is supposed to handle millions of messages per second
on commodity hardware. It also happens that Kafka producer (a component that is responsible for sending messages to Kafka)
provides non-blocking API by default (see: https://kafka.apache.org/10/javadoc/index.html?org/apache/kafka/clients/producer/KafkaProducer.html)

So, creating a Kafka client for Locust could be a time well invested!

There is accompanying article describing the process and results of creating a Kafka Client here: https://medium.com/p/b9d9e6e49537/.
Please, take a look at it. 

Below you'll find some additional technical details that can help with understanding and reproducing the experiment.

# Development environment setup

In order to be able to develop the Kafka client and test it, I need an environment with a working Kafka cluster and Locust cluster.

You can achieve it in many ways:
* connect to an existing Kafka cluster,
* have "bare metal" Kafka deployment  - in *nix world it’s quite easy
* use docker  -  there are many docker images that allow for running Kafka in Docker (https://github.com/wurstmeister/kafka-docker being one of the most popular),
* Kubernetes  - this is the option I opted for. First of all, I have already tested Locust cluster creation with K8s.

For me ,  personally , the easiest approach is to go with K8s. It manages the containers, helps mak networking right, etc.

## Setting up Kafka
I have a good experience with Debezium images of Kafka deployment on Kubernetes. So, I'll stick with it.

To create Zookeeper and Kafka node, simply do something like this:

```
> git clone https://github.com/karol-brejna-i/locust-experiments.git
> cd locust-experiments
> cd kafka-client
> kubectl create -f kubernetes/kafka/
deployment "kafka" created
service "kafka" created
deployment "zookeeper" created
service "zookeeper" created
```

## Updated Locust docker image
Some time ago I created and published small, [general purpose Locust image](https://hub.docker.com/r/grubykarol/locust/ (ATTOW the latest vesion is 0.8.1-py3.6) 

For this exercise, I decided to extend the image by installing `kafka-python` library there.

See [docker-kafka-python](docker-kafka-python) for details.

## Locust descriptors
[The scripts](kubernetes) are based on [previous experiment](https://medium.com/locust-io-experiments/locust-io-experiments-running-in-kubernetes-95447571a550). 

I introduced few changes:

* the scripts use Locust image tagged 0.8.1-py3.6-kafka (so you need to build in advance)
* all file names got `locust-` prefix
* `--print-stats` got removed -- it was too noisy
* new environment variable was introduced (`QUIET_MODE`) so the scripts can decide (based on its value) on the verbosity of logging 

## Updating configmap with latest version of scripts
This version of deployment scripts assumes that Locust test code is stored in a dedicated configmap.

When you edit the sources ([locust-scripts folder](locust-scripts)) and want to use them, the configmap should also be updated.

For me the following worked find:
```
kubectl delete cm scripts-cm
kubectl create configmap scripts-cm --from-file locust-scripts/
kubectl get cm -o yaml scripts-cm | sed '/creationTimestamp\|resourceVersion\|selfLink\|uid:/d' > kubernetes/locust/locust-scripts-cm.yaml
kubectl delete pods -l 'role in (locust-master, locust-slave)'
``` 

It's a bit rough an approach as it involves deleting the configmap, recreating it from the sources and restarting all Locust pods, but it works.

## Starting Locust
Kafka broker address is configurable. [locust-config-cm](kubernetes/locust/locust-config-cm.yaml) assumes
that comma separated kafka node addresses will be stored in `KAFKA_BROKERS` field (the default being "kafka:9092").
You'll need update it when connecting to some other cluster.

The topic name can be also changed. OUTPUT_TOPIC is used for this purpose ("test-topic" is the default).

QUIET_MODE's default value is true. The code is written in such a way, that when quiet mode is off,
atomic results (individual request info will be logged to stdout).

When everything is configured (defaults works fine, you don't need to do anything, if you don't feel to), this would work:

```
> kubectl create -f kubernetes/locust/
configmap "locust-cm" created
service "locust-external" created
ingress "locust" created
deployment "locust-master" created
configmap "scripts-cm" created
service "locust-master" created
deployment "locust-slave" created
```

# The code
See https://medium.com/p/b9d9e6e49537/ for details.