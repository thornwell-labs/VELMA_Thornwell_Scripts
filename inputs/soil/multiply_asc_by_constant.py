"""
Multiplies the data values of an ESRI ASCII grid (.asc) by a constant and
writes the result to a new .asc file, preserving the original header.
Configured here to halve humus nitrogen layers for a sensitivity test.
"""

import numpy as np

def read_asc(file_path):
    """Reads an .asc file, extracting the header and raster data."""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    header = lines[:6]  # First 6 lines contain header information
    data = np.loadtxt(lines[6:], dtype=float)  # Load raster values

    return header, data

def write_asc(output_path, header, data):
    """Writes an .asc file with the given header and raster data."""
    with open(output_path, 'w') as f:
        f.writelines(header)  # Write header unchanged
        np.savetxt(f, data, fmt='%.6f')  # Write raster data with 6 decimal precision

def multiply_asc(input_file, constant, output_file):
    """Multiplies .asc file by a constant and writes the output to a new file."""
    header1, data1 = read_asc(input_file)

    result_data = data1 * constant  # Element-wise multiplication

    write_asc(output_file, header1, result_data)

# Example usage:
root='path/to/VELMA_Watersheds/Huge/Data_Inputs30m/o_10_ChemistryPools/SOLUS_HumusN/'
constant = 0.5

for number in [1, 2, 3, 4]:
    output_file = f"{root}layer{number}_humusN_gm2_Huge_reduced_halved.asc"
    input_file = f"{root}layer{number}_humusN_gm2_Huge_reduced.asc"
    multiply_asc(input_file, constant, output_file)
