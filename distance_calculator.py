import pandas as pd
import numpy as np
from haversine import haversine

# Example DataFrame: Demand Centres
df_demand = pd.DataFrame({
    "Identifier": ["D1", "D2", "D3"],
    "Latitude": [51.5074, 51.509, 51.483],  # Example LSOA centroids
    "Longitude": [-0.1278, -0.134, -1.231],
})

# DataFrame: Brownfield Land
file_path = 'brownfield-land.csv'
# Import the CSV file into a DataFrame
df = pd.read_csv(file_path)
# Display the first few rows of the DataFrame to verify the data as a check
# print(df.head())
# Check count of rows
# print(df.count())
# Remove rows where the 'point' column has missing data
df_bb_cleaned = df.dropna(subset=['point'])
# Convert to float
df_bb_cleaned['longitude'] = pd.to_numeric(df_bb_cleaned['longitude'], errors='coerce')
df_bb_cleaned['latitude'] = pd.to_numeric(df_bb_cleaned['latitude'], errors='coerce')

# Check count of rows after cleaning
# print(df_cleaned.count())

# Calculate distances between every LSOA location and brown belt location
distances = []
for _, row_d in df_demand.iterrows():
    for _, row_bb in df_bb_cleaned.iterrows():
        distance = haversine(row_d["Latitude"], row_d["Longitude"], row_bb["latitude"], row_bb["longitude"])
        distances.append({
            "Demand_ID": row_d["Identifier"],
            "Brown_Belt_ID": row_bb["entity"],
            "Distance_km": distance
        })

# Convert results into a DataFrame
df_distances = pd.DataFrame(distances)
print(df_distances)