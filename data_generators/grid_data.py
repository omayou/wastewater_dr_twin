# data_generators/grid_data.py
import numpy as np
import pandas as pd

class GridDataGenerator:
    def __init__(self, base_demand, base_price):
        self.base_demand = base_demand
        self.base_price = base_price

    def generate_data(self, start_time, end_time, freq='5T'):
        date_range = pd.date_range(start=start_time, end=end_time, freq=freq.replace('T', 'min'))
        data = []
        for timestamp in date_range:
            hour = timestamp.hour
            # Simulate higher demand during day hours
            demand_factor = 1 + 0.5 * np.sin(np.pi * hour / 12)
            demand = self.base_demand * demand_factor * (1 + np.random.normal(0, 0.1))
            price = self.base_price * demand_factor * (1 + np.random.normal(0, 0.05))
            data.append({
                'timestamp': timestamp,
                'demand': demand,  # Changed from 'grid_demand' to 'demand'
                'price': price     # Changed from 'energy_price' to 'price'
            })
        return pd.DataFrame(data)

# Test the generator
if __name__ == "__main__":
    generator = GridDataGenerator(5000, 0.1)
    data = generator.generate_data('2024-09-26 00:00:00', '2024-09-27 00:00:00')
    print(data.head())