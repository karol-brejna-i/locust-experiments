import time

from confluent_kafka import Producer


class KafkaConfluentClient:

    def __init__(self, kafka_brokers=None):
        print("creating message sender with params: " + str(locals()))

        if kafka_brokers is None:
            kafka_brokers = ['localhost:9092']
        # XXX TODO hardcoded
        self.producer = Producer({'bootstrap.servers': 'localhost:9092'})

    def delivery_report(err, msg):
        """ Called once for each message produced to indicate delivery result.
            Triggered by poll() or flush(). """
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

    # XXX TODO needs update to use confluent-kafka
    def send(self, topic, key=None, message=None):
        print("send message")
        start_time = time.time()
        self.producer.poll()
        future = self.producer.produce(topic,
                                       key=key.encode() if key else None,
                                       value=message.encode() if message else None,
                                       callback=self.delivery_report)

    # XXX TODO needs update to use confluent-kafka
    def finalize(self):
        print("flushing the messages")
        self.producer.flush(timeout=5)
        print("flushing finished")
