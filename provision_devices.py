import requests
import json
import sys

IOT_AGENT_URL = "http://localhost:4041"

# Add these constants
FIWARE_SERVICE = "wastewater"
FIWARE_SERVICEPATH = "/"

def provision_service():
    headers = {
        'Content-Type': 'application/json',
        'fiware-service': FIWARE_SERVICE,
        'fiware-servicepath': FIWARE_SERVICEPATH
    }
    payload = {
        "services": [
            {
                "apikey": "wastewater_dr_twin_key",
                "cbroker": "http://orion:1026",
                "entity_type": "Device",
                "resource": "/iot/json"
            }
        ]
    }
    response = requests.post(f"{IOT_AGENT_URL}/iot/services", headers=headers, data=json.dumps(payload))
    print(f"Service provisioning response: {response.status_code}")
    if response.status_code != 201:
        print(f"Error details: {response.text}")
        sys.exit(1)  # Exit if service provisioning fails

def provision_device(device_id, entity_name, entity_type):
    headers = {
        'Content-Type': 'application/json',
        'fiware-service': FIWARE_SERVICE,
        'fiware-servicepath': FIWARE_SERVICEPATH
    }
    payload = {
        "devices": [
            {
                "device_id": device_id,
                "entity_name": entity_name,
                "entity_type": entity_type,
                "protocol": "json",
                "transport": "MQTT",
                "attributes": [
                    {"object_id": "power", "name": "power", "type": "Number"},
                    {"object_id": "status", "name": "status", "type": "Text"},
                    {"object_id": "efficiency", "name": "efficiency", "type": "Number"},
                    {"object_id": "dissolved_oxygen", "name": "dissolved_oxygen", "type": "Number"},
                    {"object_id": "demand", "name": "demand", "type": "Number"},
                    {"object_id": "price", "name": "price", "type": "Number"}
                ]
            }
        ]
    }
    response = requests.post(f"{IOT_AGENT_URL}/iot/devices", headers=headers, data=json.dumps(payload))
    print(f"Device {device_id} provisioning response: {response.status_code}")
    if response.status_code != 201:
        print(f"Error details: {response.text}")

if __name__ == "__main__":
    provision_service()
    for i in range(1, 6):
        provision_device(f"pump00{i}", f"urn:ngsi-ld:Pump:00{i}", "Pump")
    for i in range(1, 4):
        provision_device(f"aeration00{i}", f"urn:ngsi-ld:AerationBasin:00{i}", "AerationBasin")
    provision_device("grid001", "urn:ngsi-ld:GridDemand:001", "GridDemand")