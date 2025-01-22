import websocket
import json
import time
from datetime import datetime
from hazelcast_cluster import initialize_hazelcast_client
from topic import get_large_trades_topic, publish_large_trade
from data_processing import process_and_save_aggregated_data
import logging
from hazelcast.core import HazelcastJsonValue

logging.basicConfig(level=logging.DEBUG) 
logger = logging.getLogger(__name__)

# Inicjalizacja klienta Hazelcast
client = initialize_hazelcast_client()

# Topic dla dużych transakcji
large_trades_topic = get_large_trades_topic(client)

LARGE_TRADE_THRESHOLD = 10000.0  # Wartość transakcji (cena * wolumen > 100000)

# Inicjalizacja Generatora Flake Id
id_generator = client.get_flake_id_generator("id-generator").blocking()

# Działanie na otrzymanej wiadomości z WebSocket
def on_message(ws, message):
    try:
        data = json.loads(message)
        
        iso_time = data.get("time")
        # Wyliczenie czasu unix dla wygody zapytań SQL zapytań 
        if iso_time:
            try:
                unix_time = int(datetime.fromisoformat(iso_time.replace("Z", "+00:00")).timestamp() * 1000)
                data["time_unix"] = unix_time
            except ValueError:
                print(f"Invalid timestamp format: {iso_time}")
                data["time_unix"] = None
        else:
            data["time_unix"] = None

        # Unikalny klucz - flake_id_generator
        trade_id = id_generator.new_id()

        record = {
            "trade_id": str(trade_id),
            "product_id": data.get("product_id"),
            "price": float(data.get("price", 0)),
            "volume": float(data.get("last_size", 0)),
            "time_iso": iso_time,
            "time_unix": data.get("time_unix"),
            "side": data.get("side")  # buy/sell
        }

        #logger.debug(f"Trade ID: {trade_id}, Data: {record}")

        trade_value =  float(data.get("price", 0)) * float(data.get("last_size", 0))

        client.get_map("trades").put(str(trade_id), HazelcastJsonValue(json.dumps(record)))

        process_and_save_aggregated_data(
            client=client,
            product_id=record["product_id"],
            price=record["price"],
            volume=record["volume"]
        )

        if trade_value > LARGE_TRADE_THRESHOLD:
            publish_large_trade(large_trades_topic, json.dumps(record))
            logger.info(f"Large trade published to topic: {record}")

    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
    except Exception as e:
        print(f"Error saving trade: {e}")

# Połaczenie WebSocket
def on_open(ws):
    print("Connected to WebSocket, subscribing to channels...")
    subscribe_message = json.dumps({
        "type": "subscribe",
        "channels": [{"name": "ticker", "product_ids": ["BTC-USD", "ETH-USD"]}]
    })
    ws.send(subscribe_message)

# Obsługa błędów WebSocket
def on_error(ws, error):
    print(f"WebSocket error: {error}")

# Zamknięcie połączenia WebSocket
def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket closed. Status code: {close_status_code}, message: {close_msg}")
    client.shutdown()

# Funkcja uruchamiająca połączenie WebSocket
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
    logging.info("Application initialized.")
    start_websocket()
