import json
import asyncio

from kafka import KafkaProducer, KafkaConsumer
from bluesky.run_engine import Dispatcher

from bluesky.callbacks.core import CallbackBase


class Publisher(CallbackBase):
    """
    A callback that publishes documents to kafka.
    Parameters
    ----------
    boostrap_servers: list
        list of servers the brokers run on
    topic: str
        topic to push to
    Example
    -------
    >>> publisher = KafkaCallback('localhost:9092')
    """
    def __init__(self, bootstrap_servers, topic):
        self._publisher = KafkaProducer(bootstrap_servers=bootstrap_servers)
        self._topic = topic

    def start(self, doc):
        bs = json.dumps(doc).encode('utf-8')
        self._publisher.send(self._topic, bs)

class Consumer(Dispatcher):
    '''
    '''
    def __init__(self, bootstrap_servers, topic):
        self._task = None
        self.loop = asyncio.get_event_loop()
        self._topic = topic
        self._consumer = KafkaConsumer(topic, bootstrap_servers=bootstrap_servers)

    @asyncio.coroutine
    def _poll(self):
        while True:
            result = yield next(self._consumer)
            bs = result.value
            print("got message: {}".format(bs))
            #hostname, pid, RE_id, name, doc = message.split(b' ', 4)
            #hostname = hostname.decode()
            #pid = int(pid)
            #RE_id = int(RE_id)
            #name = name.decode()
            #if self._is_our_message(hostname, pid, RE_id):
                #doc = pickle.loads(doc)
                #self.loop.call_soon(self.process, DocumentNames[name], doc)

    def start(self):
        try:
            self._task = self.loop.create_task(self._poll())
            self.loop.run_forever()
        except:
            print("Error, stopping")
            self.stop()
            raise

    def stop(self):
        if self._task is not None:
            self._task.cancel()
            self.loop.stop()
        self._task = None


''' Callback method (to debug)
bootstrap_servers = ['cmb01:9092', 'cmb02:9092']
topic = 'qas-analysis'

prod = Publisher(bootstrap_servers=bootstrap_servers, topic=topic)
consumer = Consumer(bootstrap_servers=bootstrap_servers, topic=topic)

prod.start(dict(name="julien", msg="test"))

print("starting consumer")
consumer.start()
print("done")
'''

topic = 'qas-analysis'
send_doc = dict(name='julien', subject="test")

print("Sending {}".format(send_doc))

bs = json.dumps(send_doc).encode('utf-8')

bootstrap_servers = ['cmb01:9092', 'cmb02:9092']
consumer = KafkaConsumer(topic, bootstrap_servers=bootstrap_servers)

def receive():
    print("now receiving...")
    for bs in consumer:
        print("received {}".format(json.loads(bs.value)))


from threading import Thread
th = Thread(target=receive)
th.daemon=True

th.start()

publisher = KafkaProducer(bootstrap_servers=bootstrap_servers)
result = publisher.send(topic, bs)
print(result.get())
