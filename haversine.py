import pandas as pd
import numpy as np

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