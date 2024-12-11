from pulp import LpMaximize, LpProblem, LpVariable, lpSum
import pandas as pd
import numpy as np
from haversine import haversine
from functions import *

df_demand = create_df("demand_centres.csv")
df_brown_belt = create_df("brownfield-land.csv")

df_brown_belt = df_brown_belt[0:20]
df_demand = df_demand[0:20]

#print(calc_distances(df_demand, df_brown_belt))
#working so far

bb_locations = df_brown_belt['entity'].tolist()
demand_centres = df_demand["LSOA code"].tolist()
#demand = df_demand["Electricity Total Consumption (kWh)"] # Demand at each centre
demand = df_demand.set_index("LSOA code")["Electricity Total Consumption (kWh)"]
#df_brown_belt = df_brown_belt.set_index('entity')
capacity = df_brown_belt.set_index("entity")["plant-capacity"] # Capacity of each location
resource_potential = df_brown_belt.set_index("entity")["resource-capacity"]  # Resource potential at each location
distances_df = calc_distances(df_demand, df_brown_belt)
#print(distances_df)
distance = distances_df.set_index(['Brown_Belt_ID', 'Demand_ID'])['Distance_km'].to_dict()
#print(distance)
green_space_availability = df_brown_belt['green-space-availability'].tolist() # 1 if available, 0 otherwise

# Weights for the objective function
lambda_1 = 1  # Weight for maximising energy supply
lambda_2 = 0.5  # Weight for minimising distance costs

# Define the problem
problem = LpProblem("Renewable_Energy_Plant_Optimization", LpMaximize)
# Decision variables
x = LpVariable.dicts("Build", bb_locations, cat="Binary")  # 1 if a plant is built, 0 otherwise
print(x)
y = LpVariable.dicts("Supply", [(i, j) for i in bb_locations for j in demand_centres], lowBound=0)  # Energy supplied

# Objective function
problem += (
    lambda_1 * lpSum(y[i, j] for i in bb_locations for j in demand_centres) -
    lambda_2 * lpSum(distance[i, j] * y[i, j] for i in bb_locations for j in demand_centres)
), "Total Objective"
# Constraints

# 1. Demand satisfaction
for j in demand_centres:
    problem += lpSum(y[i, j] for i in bb_locations) >= demand[j], f"Demand_Satisfaction_{j}"

# 2. Plant capacity
for i in bb_locations:
    problem += lpSum(y[i, j] for j in demand_centres) <= capacity[i] * x[i], f"Plant_Capacity_{i}"

# 3. Green space availability
# for i in bb_locations:
#     print(i)
#     print(x[i])
#     #green_space_availability[i])
#     problem += x[i] <= green_space_availability[i], f"Green_Space_{i}"
#     print(i)

# 4. Resource potential
# for i in bb_locations:
#     problem += lpSum(y[i, j] for j in demand_centres) <= resource_potential[i], f"Resource_Potential_{i}"
# print("test output")

print("Solver:", problem.solver)

# Solve the problem
problem.solve()

# Output the results
print("Status:", problem.status)
print("Optimal Objective Value:", problem.objective.value())
print("Plant Locations:")
for i in bb_locations:
    print(f"  Build at {i}: {x[i].value()}")
print("Energy Supply:")
for i, j in y:
    print(f"  Supply from {i} to {j}: {y[i, j].value()} MW")