import time
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
import json
from data_generators.main_generator import DataGenerator
from config import *
from demand_response.algorithm import DemandResponseAlgorithm
import requests
from pandas import Timestamp
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Timestamp):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

class IoTAgent:
    def __init__(self, broker, port):
        self.client = mqtt.Client()
        self.client.connect(broker, port)
        self.client.loop_start()
        self.api_key = API_KEY

    def send_data(self, device_id, data):
        topic = f"/json/{self.api_key}/{device_id}/attrs"
        payload = json.dumps(data, default=serialize_datetime)
        self.client.publish(topic, payload)
        print(f"Published to topic {topic}: {payload}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

def send_data_to_dashboard(pumps, aeration_basins, grid):
    data = {
        'pumps': [pump.to_dict() for pump in pumps],
        'aeration_basins': [basin.to_dict() for basin in aeration_basins],
        'grid': grid.to_dict()
    }
    url = 'http://localhost:5000/update_data'
    headers = {'Content-Type': 'application/json'}
    try:
        logger.info("Sending data to dashboard")
        response = requests.post(url, 
                                 headers=headers,
                                 data=json.dumps(data, default=serialize_datetime))
        response.raise_for_status()
        logger.info("Data sent to dashboard successfully")
        logger.info(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send data to dashboard: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")

class Pump:
    def __init__(self, id, power, efficiency, status, optimized_power=None, optimized_efficiency=None, optimized_status=None):
        self.id = id
        self.power = power
        self.efficiency = efficiency
        self.status = status
        self.optimized_power = optimized_power
        self.optimized_efficiency = optimized_efficiency
        self.optimized_status = optimized_status

    def to_dict(self):
        return {
            'id': self.id,
            'power': float(self.power),
            'efficiency': float(self.efficiency),
            'status': self.status,
            'optimized_power': float(self.optimized_power) if self.optimized_power is not None else None,
            'optimized_efficiency': float(self.optimized_efficiency) if self.optimized_efficiency is not None else None,
            'optimized_status': self.optimized_status
        }

class AerationBasin:
    def __init__(self, id, power, dissolved_oxygen, optimized_power=None, optimized_dissolved_oxygen=None):
        self.id = id
        self.power = power
        self.dissolved_oxygen = dissolved_oxygen
        self.optimized_power = optimized_power
        self.optimized_dissolved_oxygen = optimized_dissolved_oxygen

    def to_dict(self):
        return {
            'id': self.id,
            'power': float(self.power),
            'dissolved_oxygen': float(self.dissolved_oxygen),
            'optimized_power': float(self.optimized_power) if self.optimized_power is not None else None,
            'optimized_dissolved_oxygen': float(self.optimized_dissolved_oxygen) if self.optimized_dissolved_oxygen is not None else None
        }

class Grid:
    def __init__(self, demand, price):
        self.demand = demand
        self.price = price

    def to_dict(self):
        return {
            'demand': float(self.demand),
            'price': float(self.price)
        }

def main():
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=SIMULATION_DURATION)
    generator = DataGenerator()
    iot_agent = IoTAgent(MQTT_BROKER, MQTT_PORT)
    dr_algorithm = DemandResponseAlgorithm()

    logger.info(f"Starting simulation at {start_time}")
    logger.info(f"Simulation will end at {end_time}")

    while datetime.now() < end_time:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"\nGenerating data for {current_time}")
        pump_data, aeration_data, grid_data = generator.generate_data(current_time, current_time)

        # Prepare data for DR algorithm
        pumps = [Pump(row['pump_id'], row['power'], row['efficiency'], row['status']) for _, row in pump_data.iterrows()]
        aeration_basins = [AerationBasin(row['basin_id'], row['power'], row['dissolved_oxygen']) for _, row in aeration_data.iterrows()]
        grid = Grid(grid_data.iloc[0]['demand'], grid_data.iloc[0]['price'])

        # Run DR algorithm
        recommendations, optimized_pumps, optimized_aeration = dr_algorithm.get_recommendations(pumps, aeration_basins, grid)

        # Print recommendations
        logger.info("Demand Response Recommendations:")
        for recommendation in recommendations:
            logger.info(f"- {recommendation}")

        # Update pumps and aeration basins with optimized data
        for i, pump in enumerate(pumps):
            pump.optimized_power = optimized_pumps[i]['power']
            pump.optimized_efficiency = optimized_pumps[i]['efficiency']
            pump.optimized_status = optimized_pumps[i]['status']

        for i, basin in enumerate(aeration_basins):
            basin.optimized_power = optimized_aeration[i]['power']
            basin.optimized_dissolved_oxygen = optimized_aeration[i]['dissolved_oxygen']

        # Send data to IoT platform
        for pump in pumps:
            data = {
                "power": {"type": "Number", "value": pump.power},
                "status": {"type": "Text", "value": pump.status},
                "efficiency": {"type": "Number", "value": pump.efficiency},
                "optimized_power": {"type": "Number", "value": pump.optimized_power},
                "optimized_status": {"type": "Text", "value": pump.optimized_status},
                "optimized_efficiency": {"type": "Number", "value": pump.optimized_efficiency}
            }
            device_id = f"pump{pump.id[-3:]}"
            iot_agent.send_data(device_id, data)

        for basin in aeration_basins:
            data = {
                "power": {"type": "Number", "value": basin.power},
                "dissolved_oxygen": {"type": "Number", "value": basin.dissolved_oxygen},
                "optimized_power": {"type": "Number", "value": basin.optimized_power},
                "optimized_dissolved_oxygen": {"type": "Number", "value": basin.optimized_dissolved_oxygen}
            }
            device_id = f"aeration{basin.id[-3:]}"
            iot_agent.send_data(device_id, data)

        # Send grid data
        data = {
            "demand": {"type": "Number", "value": grid.demand},
            "price": {"type": "Number", "value": grid.price}
        }
        device_id = "grid001"
        iot_agent.send_data(device_id, data)

        # Send data to dashboard
        send_data_to_dashboard(pumps, aeration_basins, grid)

        logger.info(f"Waiting for next update... (Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        time.sleep(UPDATE_INTERVAL)

    logger.info(f"Simulation completed at {datetime.now()}")
    iot_agent.disconnect()

if __name__ == "__main__":
    main()