import hazelcast

class HazelcastCluster:
    def __init__(self):
        print("Connecting to Hazelcast cluster...")
        self.client = hazelcast.HazelcastClient(
            cluster_name = "dev",
            cluster_members=["hazelcast-1", "hazelcast-2", "hazelcast-3"],
        )
        self.map_name = "coinbase_trades"
        self.trades_map = self.client.get_map(self.map_name).blocking()
        print(f"Connected to Hazelcast cluster. Ready to use map: {self.map_name}")

    def save_trade(self, trade_id, trade_data):
        try:
            self.trades_map.put(str(trade_id), trade_data)
            print(f"Inserted into Hazelcast IMap: {trade_id} -> {trade_data}")
        except Exception as e:
            print(f"Error inserting trade into Hazelcast IMap: {e}")

    def close(self):
        self.client.shutdown()
