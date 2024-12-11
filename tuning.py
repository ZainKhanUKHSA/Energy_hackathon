#Hyperparameter tuning for the model

import numpy as np
import itertools
import pandas as pd
from haversine import haversine
from functions import *
from sklearn.preprocessing import MinMaxScaler
from pulp import *

df_demand = create_df("demand_centres.csv")
df_brown_belt = create_df("brownfield-land.csv")

df_brown_belt = df_brown_belt[0:2000]
df_demand = df_demand[0:100]

val_ranges = [0.1, 0.25, 0.5, 0.75, 1] #np.arange(0.01, 1.01, 0.01)

results = []

# Grid search
for lambda_1, lambda_2, lambda_3 in itertools.product(val_ranges, val_ranges, val_ranges):
    objective_value, build_locations, supply_data = optimise_model(df_demand, df_brown_belt, lambda_1, lambda_2, lambda_3)
    results.append({
        "lambda_1": lambda_1,
        "lambda_2": lambda_2,
        "lambda_3": lambda_3,
        "objective_value": objective_value,
        "build_locations": build_locations,
        "supply_data": len(supply_data) # Number of locations with supply
    })

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Save results to CSV file
results_df.to_csv("hyperparameter_tuning_results.csv", index=False)

print("Results saved to hyperparameter_tuning_results.csv")