# wastewater_dr_twin/fiware_integration/iot_agent_interface.py

import paho.mqtt.client as mqtt
import json
import time

class IoTAgentInterface:
    def __init__(self, mqtt_broker, mqtt_port, api_key):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.api_key = api_key
        self.client = mqtt.Client()

    def connect(self):
        self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def send_data(self, device_id, data):
        topic = f"/json/{self.api_key}/{device_id}/attrs"
        payload = json.dumps(data)
        self.client.publish(topic, payload)
        time.sleep(0.1)  # Small delay to ensure message is sent