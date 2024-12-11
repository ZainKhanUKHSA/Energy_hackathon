import pandas as pd
import numpy as np

# Example DataFrames: Demand Centres and Brown Belt Locations
df_demand = pd.DataFrame({
    "Identifier": ["D1", "D2", "D3"],
    "Latitude": [51.5074, 51.509, 51.483],  # Example LSOA centroids
    "Longitude": [-0.1278, -0.134, -1.231],
})

df_brown_belt = pd.DataFrame({
    "Identifier": ["BB1", "BB2", "BB3"],
    "Latitude": [51.483, 51.509, 51.621],
    "Longitude": [-1.231, -0.134, -1.908],
})

# Haversine Formula for Distance Calculation
def haversine(lat1, lon1, lat2, lon2):
    # Earth radius in kilometers
    R = 6371
    # Convert degrees to radians
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    # Haversine formula
    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

# Calculate distances between every LSOA location and brown belt location
distances = []
for _, row_d in df_demand.iterrows():
    for _, row_bb in df_brown_belt.iterrows():
        distance = haversine(row_d["Latitude"], row_d["Longitude"], row_bb["Latitude"], row_bb["Longitude"])
        distances.append({
            "Demand_ID": row_d["Identifier"],
            "Brown_Belt_ID": row_bb["Identifier"],
            "Distance_km": distance
        })

# Convert results into a DataFrame
df_distances = pd.DataFrame(distances)
print(df_distances)
print("test output")