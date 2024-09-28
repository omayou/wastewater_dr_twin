# data_generators/pump_data.py
import numpy as np
import pandas as pd

class PumpDataGenerator:
    def __init__(self, pump_id, base_power, efficiency):
        self.pump_id = pump_id
        self.base_power = base_power
        self.efficiency = efficiency

    def generate_data(self, start_time, end_time, freq='5T'):
        date_range = pd.date_range(start=start_time, end=end_time, freq=freq.replace('T', 'min'))
        data = []
        for timestamp in date_range:
            power = self.base_power * (1 + np.random.normal(0, 0.1))
            status = 'running' if np.random.random() > 0.05 else 'idle'
            efficiency = self.efficiency * (1 + np.random.normal(0, 0.05))
            data.append({
                'timestamp': timestamp,
                'pump_id': self.pump_id,
                'power': power,
                'status': status,
                'efficiency': efficiency
            })
        return pd.DataFrame(data)