import hazelcast
import time

class JetStreams:
    def __init__(self, cluster_members=None):
        """Inicjalizacja klienta Hazelcast oraz obiektów mapy"""
        self.client = hazelcast.HazelcastClient(
            cluster_name = "dev",
            cluster_members=cluster_members or ["127.0.0.1:5701", "127.0.0.1:5702", "127.0.0.1:5703"]
        )
        self.trade_map = self.client.get_map("tradeEventsMap").blocking()
        self.vwap_map = self.client.get_map("vwapMap").blocking()
    
    def process_trade_event(self, trade_event):
        """
        Przetwarza wydarzenie handlowe i dodaje je do mapy Hazelcast.
        
        Parametry:
        - trade_event (dict): Dane handlowe zawierające cenę, ilość, parę walutową i czas.
        """
        pair = trade_event.get("product_id")
        trade_id = trade_event.get("trade_id")
        price = float(trade_event.get("price", 0))
        size = float(trade_event.get("size", 0))
        
        if not (pair and trade_id and price and size):
            print(f"Nieprawidłowe dane transakcji: {trade_event}")
            return
        
        trade_key = f"{pair}-{trade_id}"
        self.trade_map.put(trade_key, trade_event)
        print(f"[INFO] Dodano transakcję: {trade_key} - Cena: {price}, Ilość: {size}")
        
    def calculate_vwap(self, pair):
        """
        Oblicza VWAP (Volume Weighted Average Price) dla określonej pary handlowej.
        
        Parametry:
        - pair (str): Para walutowa (np. BTC-USD, ETH-USD)
        
        Zwraca:
        - vwap (float): Wartość VWAP dla danej pary walutowej.
        """
        trades = [value for key, value in self.trade_map.entry_set() if pair in key]
        
        if not trades:
            print(f"[INFO] Brak transakcji do obliczenia VWAP dla {pair}")
            return 0

        total_volume = 0
        total_price_volume = 0

        for trade in trades:
            price = float(trade.get("price", 0))
            size = float(trade.get("size", 0))
            total_volume += size
            total_price_volume += price * size

        if total_volume == 0:
            print(f"[INFO] Brak wolumenu dla {pair}, VWAP nie może być obliczony.")
            return 0
        
        vwap = total_price_volume / total_volume
        self.vwap_map.put(pair, vwap)
        
        print(f"[INFO] Obliczono VWAP dla {pair}: {vwap}")
        return vwap

    def start_stream_processing(self):
        """
        Metoda symulująca przetwarzanie strumieniowe. W rzeczywistości 
        powinna odbierać strumień danych (np. z WebSocket) i je przetwarzać.
        """
        try:
            while True:
                # Symulowane dane handlowe (można to podłączyć do WebSocket)
                fake_trade_event = {
                    "product_id": "BTC-USD",
                    "trade_id": int(time.time()),  # unikalny identyfikator oparty na czasie
                    "price": 30000 + (time.time() % 1000),  # cena zmienia się co sekundę
                    "size": 0.01  # losowa ilość
                }
                
                # Przetwarzanie danych handlowych
                self.process_trade_event(fake_trade_event)
                
                # Co 10 sekund obliczamy VWAP
                if int(time.time()) % 10 == 0:
                    self.calculate_vwap("BTC-USD")
                
                time.sleep(1)  # Czekamy 1 sekundę (dla symulacji)

        except KeyboardInterrupt:
            print("[INFO] Zatrzymano przetwarzanie strumieni.")
            self.shutdown()

    def shutdown(self):
        """Zamyka połączenie z Hazelcast."""
        self.client.shutdown()
        print("[INFO] Połączenie z Hazelcast zakończone.")
        

if __name__ == "__main__":
    # Uruchomienie przetwarzania strumieni
    stream_processor = JetStreams()
    stream_processor.start_stream_processing()
