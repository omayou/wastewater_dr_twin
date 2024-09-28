# data_generators/main_generator.py
from .pump_data import PumpDataGenerator
from .aeration_data import AerationDataGenerator
from .grid_data import GridDataGenerator
import pandas as pd

class DataGenerator:  # Renamed from WWTPDataGenerator to DataGenerator
    def __init__(self):
        self.pump_generators = [
            PumpDataGenerator('pump001', 100, 0.8),
            PumpDataGenerator('pump002', 120, 0.85),
            PumpDataGenerator('pump003', 90, 0.75),
            PumpDataGenerator('pump004', 110, 0.82),
            PumpDataGenerator('pump005', 105, 0.78)
        ]
        self.aeration_generators = [
            AerationDataGenerator('basin001', 200, 2.0),
            AerationDataGenerator('basin002', 220, 2.2),
            AerationDataGenerator('basin003', 210, 2.1)
        ]
        self.grid_generator = GridDataGenerator(5000, 0.1)

    def generate_data(self, start_time, end_time, freq='5T'):
        pump_data = pd.concat([gen.generate_data(start_time, end_time, freq) for gen in self.pump_generators])
        aeration_data = pd.concat([gen.generate_data(start_time, end_time, freq) for gen in self.aeration_generators])
        grid_data = self.grid_generator.generate_data(start_time, end_time, freq)
        
        return pump_data, aeration_data, grid_data

# Usage example:
if __name__ == "__main__":
    generator = DataGenerator()  # Updated to use the new class name
    pump_data, aeration_data, grid_data = generator.generate_data('2024-09-26 00:00:00', '2024-09-27 00:00:00')
    print(pump_data.head())
    print(aeration_data.head())
    print(grid_data.head())