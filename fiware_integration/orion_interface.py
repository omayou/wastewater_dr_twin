# wastewater_dr_twin/fiware_integration/orion_interface.py

import requests
import json

class OrionInterface:
    def __init__(self, orion_url):
        self.orion_url = orion_url

    def create_entity(self, entity):
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f"{self.orion_url}/v2/entities", headers=headers, data=json.dumps(entity))
        return response.status_code == 201

    def update_entity(self, entity_id, attributes):
        headers = {'Content-Type': 'application/json'}
        response = requests.patch(f"{self.orion_url}/v2/entities/{entity_id}/attrs", headers=headers, data=json.dumps(attributes))
        return response.status_code == 204

    def get_entity(self, entity_id):
        response = requests.get(f"{self.orion_url}/v2/entities/{entity_id}")
        if response.status_code == 200:
            return response.json()
        return None

    def delete_entity(self, entity_id):
        response = requests.delete(f"{self.orion_url}/v2/entities/{entity_id}")
        return response.status_code == 204