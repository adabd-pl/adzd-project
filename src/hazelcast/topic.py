# topic.py
from hazelcast.core import HazelcastJsonValue

# Topic dla dużych transakcji
def get_large_trades_topic(client):
    return client.get_topic("large_trades")

def publish_large_trade(topic, record):
    topic.publish(HazelcastJsonValue(record))
