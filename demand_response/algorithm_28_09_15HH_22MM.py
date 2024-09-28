# wastewater_dr_twin/demand_response/demand_response_algorithm.py

import numpy as np
from scipy.optimize import minimize

class DemandResponseAlgorithm:
    def __init__(self):
        self.pump_efficiency_threshold = 0.75
        self.do_lower_limit = 1.5
        self.do_upper_limit = 2.5
        self.max_power_reduction = 0.3  # Maximum 30% power reduction

    def optimize(self, pumps, aeration_basins, grid_data):
        current_total_power = sum(pump['power'] for pump in pumps) + sum(basin['power'] for basin in aeration_basins)
        
        # Define objective function
        def objective(x):
            new_total_power = sum(x[:len(pumps)]) + sum(x[len(pumps):])
            power_reduction = (current_total_power - new_total_power) / current_total_power
            return -power_reduction  # Minimize negative power reduction (maximize reduction)

        # Define constraints
        constraints = []
        
        # Pump constraints
        for i, pump in enumerate(pumps):
            constraints.append({'type': 'ineq', 'fun': lambda x, i=i: x[i] - pump['power'] * (1 - self.max_power_reduction)})
            constraints.append({'type': 'ineq', 'fun': lambda x, i=i: pump['power'] - x[i]})
        
        # Aeration basin constraints
        for i, basin in enumerate(aeration_basins):
            j = i + len(pumps)
            constraints.append({'type': 'ineq', 'fun': lambda x, j=j: x[j] - basin['power'] * (1 - self.max_power_reduction)})
            constraints.append({'type': 'ineq', 'fun': lambda x, j=j: basin['power'] - x[j]})
        
        # Initial guess
        x0 = [pump['power'] for pump in pumps] + [basin['power'] for basin in aeration_basins]
        
        # Solve optimization problem
        result = minimize(objective, x0, method='SLSQP', constraints=constraints)
        
        # Process results
        optimized_pumps = []
        optimized_aeration = []
        
        for i, pump in enumerate(pumps):
            new_power = result.x[i]
            new_efficiency = pump['efficiency'] * (pump['power'] / new_power)  # Assuming efficiency scales linearly
            optimized_pumps.append({
                'id': pump['id'],
                'power': new_power,
                'efficiency': new_efficiency,
                'status': 'running' if new_power > 0 else 'idle'
            })
        
        for i, basin in enumerate(aeration_basins):
            j = i + len(pumps)
            new_power = result.x[j]
            new_do = basin['dissolved_oxygen'] * (new_power / basin['power'])  # Assuming DO scales linearly with power
            optimized_aeration.append({
                'id': basin['id'],
                'power': new_power,
                'dissolved_oxygen': new_do
            })
        
        return optimized_pumps, optimized_aeration

    def get_recommendations(self, pumps, aeration_basins, grid_data):
        optimized_pumps, optimized_aeration = self.optimize(pumps, aeration_basins, grid_data)
        
        recommendations = []
        
        for pump, opt_pump in zip(pumps, optimized_pumps):
            if opt_pump['power'] < pump['power']:
                recommendations.append(f"Reduce power of Pump {pump['id']} from {pump['power']:.2f} to {opt_pump['power']:.2f}")
            elif opt_pump['power'] > pump['power']:
                recommendations.append(f"Increase power of Pump {pump['id']} from {pump['power']:.2f} to {opt_pump['power']:.2f}")
        
        for basin, opt_basin in zip(aeration_basins, optimized_aeration):
            if opt_basin['power'] < basin['power']:
                recommendations.append(f"Reduce power of Aeration Basin {basin['id']} from {basin['power']:.2f} to {opt_basin['power']:.2f}")
            elif opt_basin['power'] > basin['power']:
                recommendations.append(f"Increase power of Aeration Basin {basin['id']} from {basin['power']:.2f} to {opt_basin['power']:.2f}")
        
        return recommendations, optimized_pumps, optimized_aeration