import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the results from the CSV file
results_df = pd.read_csv("hyperparameter_tuning_results.csv")

# Ensure objective columns are numeric
results_df["objective_value"] = pd.to_numeric(results_df["objective_value"], errors="coerce")

# Drop rows with missing or invalid values
results_df = results_df.dropna(subset=["objective_value"])

# Convert objective_value to numeric 
results_df["objective_value"] = results_df["objective_value"].astype(float)
print("test")
#### CHECK ABOVE HERE FIRST

# Sort by the first objective (ascending for minimization or descending for maximization)
results_df = results_df.sort_values(by="objective_value", ascending=False)

# Initialize Pareto front
pareto_front = []

# Identify Pareto optimal points
current_best = -np.inf
for index, row in results_df.iterrows():
    if row["distance_penalty"] < current_best:
        continue
    pareto_front.append(row)
    current_best = row["distance_penalty"]

pareto_front_df = pd.DataFrame(pareto_front)
