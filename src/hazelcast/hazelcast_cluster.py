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
            "hazelcast-1",
            "hazelcast-2",
            "hazelcast-3"
        ]
    )
    logger.info("Hazelcast client initialized.")
    return client
