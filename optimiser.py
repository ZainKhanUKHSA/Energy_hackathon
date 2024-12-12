from pulp import LpMaximize, PULP_CBC_CMD, LpProblem, LpVariable, lpSum, LpStatus, value
import pandas as pd
import numpy as np
from haversine import haversine
from functions import *
from sklearn.preprocessing import MinMaxScaler

df_demand = create_df("data/demand_centres.csv")
df_brown_belt = create_df("data/brownfield-land.csv")

df_brown_belt = df_brown_belt[0:2000]
df_demand = df_demand[0:100]

#print(calc_distances(df_demand, df_brown_belt))
#working so far

# Normalise the data
scaler = MinMaxScaler()

# Normalize demand
df_demand["Normalised_Demand"] = scaler.fit_transform(df_demand[["Electricity Total Consumption (kWh)"]])

# Normalize plant capacity
df_brown_belt["Normalised_Capacity"] = scaler.fit_transform(df_brown_belt[["plant-capacity"]])

bb_locations = df_brown_belt['entity'].tolist()
demand_centres = df_demand["LSOA code"].tolist()
#demand = df_demand["Electricity Total Consumption (kWh)"] # Demand at each centre
demand = df_demand.set_index("LSOA code")["Normalised_Demand"]
#df_brown_belt = df_brown_belt.set_index('entity')
capacity = df_brown_belt.set_index("entity")["Normalised_Capacity"] # Capacity of each location
#resource_potential = df_brown_belt.set_index("entity")["resource-capacity"]  # Resource potential at each location
distances_df = calc_distances(df_demand, df_brown_belt)
#print(distances_df)
#normalise distance
distances_df["Normalised_Distances"] = scaler.fit_transform(distances_df[["Distance_km"]])
distance = distances_df.set_index(['Brown_Belt_ID', 'Demand_ID'])['Normalised_Distances'].to_dict()
#print(distance)
#green_space_availability = df_brown_belt['green-space-availability'].tolist() # 1 if available, 0 otherwise
green_space_availability = df_brown_belt.set_index("entity")['green-space-availability'].to_dict()


# Weights for the objective function
lambda_1 = 1  # Weight for maximising energy supply
lambda_2 = 1  # Weight for minimising distance costs
lambda_3 = 0.01 # Weight for minimising the number of developments

# Define the problem
problem = LpProblem("Renewable_Energy_Plant_Optimization", LpMaximize)

# Decision variables
x = LpVariable.dicts("Build", bb_locations, cat="Binary")  # 1 if a plant is built, 0 otherwise
y = LpVariable.dicts("Supply", [(i, j) for i in bb_locations for j in demand_centres], lowBound=0)  # Energy supplied

# Objective function
problem += (
    lambda_1 * lpSum(y[i, j] for i in bb_locations for j in demand_centres) -
    lambda_2 * lpSum(distance[i, j] * y[i, j] for i in bb_locations for j in demand_centres) -
    lambda_3 * lpSum(x[i] for i in bb_locations)
), "Total Objective"
# Constraints

# 1. Demand satisfaction
# for j in demand_centres:
#     problem += lpSum(y[i, j] for i in bb_locations) >= demand[j], f"Demand_Satisfaction_{j}"

# 2. Plant capacity
for i in bb_locations:
    problem += lpSum(y[i, j] for j in demand_centres) <= capacity[i] * x[i], f"Plant_Capacity_{i}"

# 3. Green space availability
#for i in bb_locations:
#    problem += x[i] <= green_space_availability[bb_locations.index(i)], f"Green_Space_{i}"
# 3. Green space availability
for i in bb_locations:
    problem += x[i] <= green_space_availability[i], f"Green_Space_{i}"

# 4. Resource potential
# for i in bb_locations:
#     problem += lpSum(y[i, j] for j in demand_centres) <= resource_potential[i], f"Resource_Potential_{i}"
# print("test output")

# Solve the problem with CBC solver
problem.solve(PULP_CBC_CMD())

# Collect results
build_locations = [i for i in bb_locations if x[i].value() == 1]
not_build_locations = [i for i in bb_locations if x[i].value() == 0]
supply_data = []
for i, j in y:
    supply_value = y[i, j].value()
    if supply_value is not None and supply_value > 0:
        supply_data.append({"Brown_Belt_ID": i, "Demand_ID": j, "Supply_MW": supply_value})

# Save results to files
build_df = pd.DataFrame({"Build_Location": build_locations})
not_build_df = pd.DataFrame({"Not_Build_Location": not_build_locations})
supply_df = pd.DataFrame(supply_data)

build_df.to_csv("optimiser_output/build_locations.csv", index=False)
not_build_df.to_csv("optimiser_output/not_build_locations.csv", index=False)
supply_df.to_csv("optimiser_output/supply_data.csv", index=False)

# Output status
print("Status:", LpStatus[problem.status])
print("Optimal Objective Value:", value(problem.objective))
print("Build Locations saved to optimiser_output/build_locations.csv")
print("Not Build Locations saved to optimiser_output/not_build_locations.csv")
print("Supply Data saved to optimiser_output/supply_data.csv")