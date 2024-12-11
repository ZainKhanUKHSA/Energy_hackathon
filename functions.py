import pandas as pd
import numpy as np
from haversine import haversine
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