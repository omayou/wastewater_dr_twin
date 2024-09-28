# wastewater_dr_twin/config.py

ORION_URL = "http://localhost:1026"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
API_KEY = "wastewater_dr_twin_key"

# Entity types
PUMP_TYPE = "Pump"
AERATION_BASIN_TYPE = "AerationBasin"
GRID_DEMAND_TYPE = "GridDemand"

# MQTT topics
PUMP_TOPIC = f"/json/{API_KEY}/pump/attrs"
AERATION_TOPIC = f"/json/{API_KEY}/aeration/attrs"
GRID_TOPIC = f"/json/{API_KEY}/grid/attrs"