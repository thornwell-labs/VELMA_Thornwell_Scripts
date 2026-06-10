"""
Filters failed outlets out of a VELMA outlet list. Reads a CSV containing the
full outlet list and a list of failed outlets, and writes a new CSV with the
failed ones removed.
"""

import pandas as pd

df = pd.read_csv("path/to/VELMA_Watersheds/Dungeness/outlet_list.csv")

full_outlets = df["Full outlet list"].tolist()
failed = df["Failed"].tolist()

new_outlets = [outlet for outlet in full_outlets if outlet not in failed]

# Pad new_outlets column to match the length of the df
while len(new_outlets) < len(df):
    new_outlets.append(None) 

df["New outlet list"] = new_outlets
df.to_csv("path/to/VELMA_Watersheds/Dungeness/new_outlet_list.csv", index=False)
        
print(new_outlets)