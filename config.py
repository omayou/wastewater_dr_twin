# wastewater_dr_twin/config.py

# FIWARE components configuration
ORION_URL = "http://localhost:1026"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
API_KEY = "wastewater_dr_twin_key"

FIWARE_SERVICE = "wastewater"
FIWARE_SERVICEPATH = "/"

# Entity types
PUMP_TYPE = "Pump"
AERATION_BASIN_TYPE = "AerationBasin"
GRID_DEMAND_TYPE = "GridDemand"

# MQTT topics
PUMP_TOPIC = f"/json/{API_KEY}/pump/attrs"
AERATION_TOPIC = f"/json/{API_KEY}/aeration/attrs"
GRID_TOPIC = f"/json/{API_KEY}/grid/attrs"

# Simulation parameters
SIMULATION_DURATION = 60  # minutes
UPDATE_INTERVAL = 60  # seconds

# Pump configuration
NUM_PUMPS = 5
PUMP_POWER_RANGE = (50, 200)  # kW
PUMP_EFFICIENCY_RANGE = (0.6, 0.9)

# Aeration basin configuration
NUM_AERATION_BASINS = 3
AERATION_POWER_RANGE = (100, 500)  # kW
DISSOLVED_OXYGEN_RANGE = (0.5, 8.0)  # mg/L

# Grid configuration
GRID_DEMAND_RANGE = (1000, 5000)  # kW
ENERGY_PRICE_RANGE = (0.05, 0.20)  # $/kWh

# Random seed for reproducibility (optional)
RANDOM_SEED = 42