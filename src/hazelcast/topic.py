from hazelcast.core import HazelcastJsonValue

# Topic dla dużych transakcji
def get_large_trades_topic(client):
    return client.get_topic("topic")

def publish_large_trade(topic, record):
    topic.publish(str(record))
