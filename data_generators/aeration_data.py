# data_generators/aeration_data.py
import numpy as np
import pandas as pd

class AerationDataGenerator:
    def __init__(self, basin_id, base_power, base_do):
        self.basin_id = basin_id
        self.base_power = base_power
        self.base_do = base_do

    def generate_data(self, start_time, end_time, freq='5T'):
        date_range = pd.date_range(start=start_time, end=end_time, freq=freq.replace('T', 'min'))
        data = []
        for timestamp in date_range:
            power = self.base_power * (1 + np.random.normal(0, 0.1))
            do_level = self.base_do * (1 + np.random.normal(0, 0.2))
            data.append({
                'timestamp': timestamp,
                'basin_id': self.basin_id,
                'power': power,
                'dissolved_oxygen': do_level
            })
        return pd.DataFrame(data)