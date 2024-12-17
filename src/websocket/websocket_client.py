import websocket
import json
import time
from src.hazelcast.hazelcast_cluster import HazelcastCluster

hazelcast_cluster = HazelcastCluster()

def on_message(ws, message):
    """Odebranie wiadomości z serwera Coinbase."""
    try:
        data = json.loads(message)
        print("Received:", data)

     
        trade_id = data.get("sequence", int(time.time() * 1000))  # Używamy "sequence" lub timestamp
        hazelcast_cluster.save_trade(trade_id, data)  # Przesyłanie do Hazelcast IMap

    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")

def on_open(ws):
    """Subskrypcja kanałów ticker dla BTC-USD i ETH-USD."""
    print("Connected to WebSocket, subscribing to channels...")
    subscribe_message = json.dumps({
        "type": "subscribe",
        "channels": [{"name": "ticker", "product_ids": ["BTC-USD", "ETH-USD"]}]
    })
    ws.send(subscribe_message)

def on_error(ws, error):
    """Obsługa błędów WebSocket."""
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    """Obsługa zamknięcia połączenia."""
    print(f"WebSocket closed. Status code: {close_status_code}, message: {close_msg}")
    hazelcast_cluster.close()  # Zamknięcie połączenia z Hazelcastem

def start_websocket():
    """Uruchom połączenie WebSocket i automatycznie połącz ponownie w razie problemów."""
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
