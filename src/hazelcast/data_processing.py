import json
import time
from collections import defaultdict
from hazelcast.core import HazelcastJsonValue

aggregation_data = defaultdict(lambda: {"total_price": 0.0, "total_volume": 0.0, "count": 0})

# Przetwarzanie danych dla mapy zagregowanej
def process_and_save_aggregated_data(client, product_id, price, volume):
    try:
        # Aktualizacja danych w słowniku
        agg_data = aggregation_data[product_id]
        agg_data["total_price"] += price * volume
        agg_data["total_volume"] += volume
        agg_data["count"] += 1

        average_price = agg_data["total_price"] / agg_data["total_volume"] if agg_data["total_volume"] > 0 else 0.0

        record = {
            "product_id": product_id,
            "average_price": average_price,
            "total_volume": agg_data["total_volume"],
            "last_updated": int(time.time() * 1000)  # czas w ms
        }

        client.get_map("aggregated_trades").put(product_id, HazelcastJsonValue(json.dumps(record)))
        print(f"Aggregated data saved for {product_id}: {record}")

    except Exception as e:
        print(f"Error processing aggregated data: {e}")
