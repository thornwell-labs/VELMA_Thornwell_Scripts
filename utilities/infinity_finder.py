"""
Scans every outlet result folder of a VELMA parallel run for 'Infinity' values
in DailyResults.csv, flagging folders where the model produced non-finite
output. Quick diagnostic for unstable runs.
"""

import os

# Define the base directory
base_dir = 'path/to/network_share/Dungeness_Data/Results/MULTI_WA_Dungeness_30m_2Oct2024/'

# Iterate through each folder in the directory
for folder in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder)

    # Check if it is a directory
    if os.path.isdir(folder_path):
        file_path = os.path.join(folder_path, 'DailyResults.csv')

        # Check if the file exists
        if os.path.exists(file_path):
            with open(file_path) as file:
                lines = file.readlines()

                # Loop through each line and check for 'Infinity'
                for line in lines:
                    if 'Infinity' in line:
                        print(f'Infinity in {folder}')
                        break  # Stop checking once 'Infinity' is found in this file
        else:
            print(f"'DailyResults.csv' not found in {folder_path}")
    else:
        print(f"{folder} is not a directory")
