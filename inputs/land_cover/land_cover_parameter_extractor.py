"""
Extracts per-cover-type parameters from a VELMA simulation configuration XML
and writes them to a CSV table for review. Filter the extracted parameters by
editing the substring match (e.g. 'Recovery').
"""

import xml.etree.ElementTree as ET
import pandas as pd

# Load the XML file
tree = ET.parse('path/to/VELMA_Watersheds/Samish/XMLs/WA_Samish30m_22Jan2025.xml')
root = tree.getroot()

# Initialize a dictionary to store cover data
cover_data = {}

# Find all 'cover' elements
for cover in root.findall('.//cover'):
    # Iterate over each cover type within 'cover'
    for cover_type in cover:
        # Extract the cover name
        cover_name = cover_type.tag
        # Initialize a dictionary for parameters of the current cover type
        cover_data[cover_name] = {}

        # Extract parameters for each cover type
        for param in cover_type:
            if 'Recovery' in param.tag:  # filter by parameter names that contain this text
                # Store each parameter as a column
                cover_data[cover_name][param.tag] = param.text

# Convert the data into a pandas DataFrame for better visualization
df = pd.DataFrame.from_dict(cover_data, orient='index')
df.to_csv('path/to/VELMA_Watersheds/Samish/XMLs/lc_table.csv')

# Display the DataFrame
print(df)
