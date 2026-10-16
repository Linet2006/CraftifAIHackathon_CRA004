"""
Workplace Safety Sentinel - MQTT Telemetry & Event Publisher
Streams high-frequency vision inference events, zone breaches, and telemetry.
"""

import json
import logging
import threading
from typing import Optional

try:
    import paho.mqtt.client as mqtt
    PAHO_AVAILABLE = True
except ImportError:
    PAHO_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] (MQTT) %(message)s")

class SafetyMQTTClient:
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883, client_id: str = "sentinel_edge_agent"):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id
        self.connected = False
        self.client = None
        self.message_history = []
        self._lock = threading.Lock()
        self.init_client()

    def init_client(self):
        if not PAHO_AVAILABLE:
            logging.warning("paho-mqtt not installed. Operating in in-memory MQTT simulation mode.")
            return

        try:
            self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv311)
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            # Connect with short timeout so it doesn't hang if no local broker is running
            self.client.connect_async(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            logging.info(f"MQTT Broker at {self.broker_host}:{self.broker_port} unavailable ({e}). Using in-memory event bus.")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logging.info(f"Successfully connected to MQTT Broker at {self.broker_host}:{self.broker_port}")
        else:
            self.connected = False

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False

    def publish_event(self, topic: str, payload: dict):
        payload_str = json.dumps(payload)
        with self._lock:
            self.message_history.append({"topic": topic, "payload": payload, "timestamp": payload.get("timestamp")})
            if len(self.message_history) > 100:
                self.message_history.pop(0)

        if self.connected and self.client:
            try:
                self.client.publish(topic, payload_str, qos=1)
            except Exception as e:
                logging.error(f"Failed to publish to MQTT broker: {e}")

    def get_recent_messages(self, limit: int = 20):
        with self._lock:
            return list(self.message_history[-limit:])

# Global singleton
mqtt_service = SafetyMQTTClient()
