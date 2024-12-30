import websocket
import json
import time
from src.hazelcast.hazelcast_cluster import HazelcastCluster

hazelcast_cluster = HazelcastCluster()

def on_message(ws, message):
    try:
        data = json.loads(message)
        print("Received:", data)


        trade_id = int(data.get("sequence", int(time.time() * 1000)))

        hazelcast_data = {
            "__key": trade_id,  
            "type": data.get("type"),
            "product_id": data.get("product_id"),
            "price": data.get("price"),
            "open_24h": data.get("open_24h"),
            "volume_24h": data.get("volume_24h"),
            "low_24h": data.get("low_24h"),
            "high_24h": data.get("high_24h"),
            "volume_30d": data.get("volume_30d"),
            "best_bid": data.get("best_bid"),
            "best_bid_size": data.get("best_bid_size"),
            "best_ask": data.get("best_ask"),
            "best_ask_size": data.get("best_ask_size"),
            "side": data.get("side"),
            "time": data.get("time"),
            "trade_id": trade_id,
            "last_size": data.get("last_size"),
        }

 
        hazelcast_cluster.save_trade(trade_id, data)  
    
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
    except Exception as e:
        print(f"Error saving trade: {e}")

def on_open(ws):
    print("Connected to WebSocket, subscribing to channels...")
    subscribe_message = json.dumps({
        "type": "subscribe",
        "channels": [{"name": "ticker", "product_ids": ["BTC-USD", "ETH-USD"]}]
    })
    ws.send(subscribe_message)

def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket closed. Status code: {close_status_code}, message: {close_msg}")
    hazelcast_cluster.close() 

def start_websocket():
    while True:
        try:
            print("Starting WebSocket connection...")
            ws = websocket.WebSocketApp(
                "wss://ws-feed.exchange.coinbase.com", 
                on_message=on_message, 
                on_open=on_open, 
                on_error=on_error, 
                on_close=on_close
            )
            ws.run_forever()
        except Exception as e:
            print(f"Error occurred: {e}. Reconnecting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    start_websocket()
