"""
Multiplies two ESRI ASCII grids (.asc) cell-by-cell and writes the result to a
new .asc file. Both inputs must share the same extent and resolution.
Configured here to apply nitrogen reduction fractions to humus nitrogen layers.
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

def multiply_asc(file1, file2, output_file):
    """Multiplies two .asc files and writes the output to a new file."""
    header1, data1 = read_asc(file1)
    header2, data2 = read_asc(file2)

    if header1 != header2:
        raise ValueError("Headers do not match. Ensure both .asc files have the same spatial extent and resolution.")

    result_data = data1 * data2  # Element-wise multiplication

    write_asc(output_file, header1, result_data)

# Example usage:
root='path/to/VELMA_Watersheds/Sammamish/Data_Inputs30m/o_10_ChemistryPools/SOLUS_HumusN/'
file1 = f"{root}nitrogen_reduction_fractions_Sammamish.asc"

for number in [1, 2, 3, 4]:
    file2 = f"{root}layer{number}_humusN_gm2_Sammamish.asc"
    output_file = f"{root}layer{number}_humusN_gm2_Sammamish_reduced.asc"
    multiply_asc(file1, file2, output_file)
    print(f'Layer {number} done')
print('Complete.')