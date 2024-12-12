import pandas as pd
import numpy as np
from haversine import haversine
from pulp import *
from sklearn.preprocessing import MinMaxScaler

def create_df(file):
    file_path = file
    # Import the CSV file into a DataFrame
    df = pd.read_csv(file_path)
    if file == "demand_centres.csv":
        df_cleaned = df
    else:    
        # Remove rows where the 'point' column has missing data 
        df_cleaned = df.dropna(subset=['point'])
    # Convert to float
    df_cleaned['longitude'] = pd.to_numeric(df_cleaned['longitude'], errors='coerce')
    df_cleaned['latitude'] = pd.to_numeric(df_cleaned['latitude'], errors='coerce')
    return df_cleaned

def calc_distances(df_demand, df_bb):
    # Calculate distances between every LSOA location and brown belt location
    distances = []
    for _, row_d in df_demand.iterrows():
        for _, row_bb in df_bb.iterrows():
            distance = haversine(row_d["latitude"], row_d["longitude"], row_bb["latitude"], row_bb["longitude"])
            distances.append({
                "Demand_ID": row_d["LSOA code"],
                "Brown_Belt_ID": row_bb["entity"],
                "Distance_km": distance
            })
    # Convert results into a DataFrame
    df_distances = pd.DataFrame(distances)
    return df_distances

def optimise_model(df_demand, df_brown_belt, lambda_1, lambda_2, lambda_3):
        
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

    
    # Define the problem
    problem = LpProblem("Renewable_Energy_Plant_Optimization", LpMaximize)

    # Decision variables
    x = LpVariable.dicts("Build", bb_locations, cat="Binary")  # Binary variable for plant build
    y = LpVariable.dicts("Supply", [(i, j) for i in bb_locations for j in demand_centres], lowBound=0)  # Energy supplied

    # Objective function
    problem += (
        lambda_1 * lpSum(y[i, j] for i in bb_locations for j in demand_centres) -
        lambda_2 * lpSum(distance[i, j] * y[i, j] for i in bb_locations for j in demand_centres) -
        lambda_3 * lpSum(x[i] for i in bb_locations)
    ), "Composite Objective"

    # Constraints
    # for j in demand_centres:
    #     problem += lpSum(y[i, j] for i in bb_locations) >= demand[j], f"Demand_Satisfaction_{j}"

    for i in bb_locations:
        problem += lpSum(y[i, j] for j in demand_centres) <= capacity[i] * x[i], f"Plant_Capacity_{i}"

    for i in bb_locations:
        problem += x[i] <= green_space_availability[i], f"Green_Space_{i}"

    # Solve the problem
    problem.solve(PULP_CBC_CMD())

    # Collect results
    build_locations = [i for i in bb_locations if x[i].value() == 1]
    supply_data = {(i, j): y[i, j].value() for i, j in y if y[i, j].value() > 0}

    # Return objective value and decision variables
    return value(problem.objective), build_locations, supply_data