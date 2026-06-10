"""
Computes summary statistics (min, max, mean) for every .asc raster in a
directory and writes them to a CSV. Quick QC tool for inspecting a folder of
grids.
"""

import os
import numpy as np
import pandas as pd

def read_asc_file(file_path):
    with open(file_path, 'r') as f:
        header_lines = []
        for _ in range(6):  # Skip the 6 header lines
            header_lines.append(f.readline())
        data = np.loadtxt(f)
    return data

def process_asc_files(directory, output_csv):
    rows = []
    for file in os.listdir(directory):
        if file.endswith(".asc"):
            file_path = os.path.join(directory, file)
            data = read_asc_file(file_path)
            
            min_val = np.min(data)
            max_val = np.max(data)
            avg_val = np.mean(data)
            
            rows.append([file, min_val, max_val, avg_val])
    
    df = pd.DataFrame(rows, columns=["File Name", "Minimum", "Maximum", "Average"])
    df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")

# Specify the directory and output file
input_directory = "path/to/VELMA_Watersheds/Quilcene/Data_Inputs30m/m_3_Age"
output_csv = "path/to/VELMA_Watersheds/Quilcene/Analysis/age_asc_statistics.csv"

process_asc_files(input_directory, output_csv)
