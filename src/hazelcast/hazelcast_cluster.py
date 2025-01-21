from hazelcast import HazelcastClient
from hazelcast.core import HazelcastJsonValue
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Inicjalizacja klienta Hazelcast
def initialize_hazelcast_client():
    client = HazelcastClient(
        flake_id_generators={
            "id-generator": {
                "prefetch_count": 50,
                "prefetch_validity": 30,
            }
        },
        cluster_members=[
            "172.19.0.2:5701",
            "172.19.0.3:5701",
            "172.19.0.4:5701"
        ]
    )
    logger.info("Hazelcast client initialized.")
    return client
