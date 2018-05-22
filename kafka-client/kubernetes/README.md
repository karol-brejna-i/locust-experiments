## Setting up Kafka
This descriptors rely on Debezium images for Kafka and Zookeeper.

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
Some time ago I created and published small, [general purpose Locust image](https://hub.docker.com/r/grubykarol/locust/) (ATTOW the latest version is 0.8.1-py3.6)

For this exercise, I decided to extend the image by installing `kafka-python` library there.

See [docker-kafka-python](../docker-kafka-python) for details.

## Locust descriptors
[The scripts](locust) are based on [previous experiment](https://medium.com/locust-io-experiments/locust-io-experiments-running-in-kubernetes-95447571a550).

I introduced few changes:

* the scripts use Locust image tagged 0.8.1-py3.6-kafka (so you need to build it in advance)
* all file names got `locust-` prefix
* `--print-stats` got removed - it was too noisy
* new environment variable was introduced (`QUIET_MODE`) so the scripts can decide (based on its value) on the verbosity of logging 
* new environment variable was introduced (`TASK_DELAY`) which the scripts can use to set up delay between tasks

## Updating configmap with latest version of scripts
This version of deployment scripts assumes that Locust test code is stored in a dedicated configmap.

When you edit the sources ([locust-scripts folder](../locust-scripts)) and want to use them, the configmap should also be updated.

For me the following worked fine (it assumes you are in locust-experiments/kafka-client folder):
```
kubectl delete cm scripts-cm
kubectl create configmap scripts-cm --from-file locust-scripts/
kubectl get cm -o yaml scripts-cm | sed '/creationTimestamp\|resourceVersion\|selfLink\|uid:/d' > kubernetes/locust/locust-scripts-cm.yaml
kubectl delete pods -l 'role in (locust-master, locust-slave)'
``` 

It's a bit rough an approach as it involves deleting the configmap, recreating it from the sources and restarting all Locust pods, but it works.

## Starting Locust
Kafka broker address is configurable. [locust-config-cm](locust/locust-config-cm.yaml) assumes
that comma separated kafka node addresses will be stored in `KAFKA_BROKERS` field (the default being "kafka:9092").
You'll need update it when connecting to some other cluster.

The topic name can be also changed. `OUTPUT_TOPIC` is used for this purpose ("test-topic" is the default).

QUIET_MODE's default value is true. The code is written in such a way, that when quiet mode is off,
atomic results (individual request info) will be logged to stdout.

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
