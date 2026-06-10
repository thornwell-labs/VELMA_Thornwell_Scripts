"""
Plots a chosen variable (e.g. biomass nitrogen) from VELMA cell data writer
CSVs, comparing the same cells across two simulation runs (here, before and
after a Michaelis-Menten uptake parameter change).
"""

import pandas as pd
import matplotlib.pyplot as plt

initial_file_paths =[r'path\to\VELMA_Watersheds\Huge\Results\MULTI_WA_Huge30m_9Dec2024\Results_75524\Cell_i46596_x83_y193_Wetlands_46596.csv',
              r'path\to\VELMA_Watersheds\Huge\Results\MULTI_WA_Huge30m_9Dec2024\Results_75524\Cell_i51444_x111_y213_DevelopedLowIntensity_51444.csv',
              r'path\to\VELMA_Watersheds\Huge\Results\MULTI_WA_Huge30m_9Dec2024\Results_75524\Cell_i59611_x84_y247_EvergreenForest_59611.csv',
              r'path\to\VELMA_Watersheds\Huge\Results\MULTI_WA_Huge30m_9Dec2024\Results_45390\Cell_i13357_x102_y55_EvergreenForest_13357.csv']
reduced_uptake_file_paths = [r'path\to\VELMA_Watersheds\Huge\Results\MULTI_WA_Huge30m_13Dec2024\Results_75524\Cell_i46596_x83_y193_Wetlands_46596.csv',
                             r'path\to\VELMA_Watersheds\Huge\Results\MULTI_WA_Huge30m_13Dec2024\Results_75524\Cell_i51444_x111_y213_DevelopedLowIntensity_51444.csv',
                             r'path\to\VELMA_Watersheds\Huge\Results\MULTI_WA_Huge30m_13Dec2024\Results_75524\Cell_i59611_x84_y247_EvergreenForest_59611.csv',
                             r'path\to\VELMA_Watersheds\Huge\Results\MULTI_WA_Huge30m_13Dec2024\Results_45390\Cell_i13357_x102_y55_EvergreenForest_13357.csv',
                             r'path\to\VELMA_Watersheds\Huge\Results\MULTI_WA_Huge30m_13Dec2024\Results_75524\Cell_i53357_x96_y221_DevelopedMediumIntensity_53357.csv',
                             r'path\to\VELMA_Watersheds\Huge\Results\MULTI_WA_Huge30m_13Dec2024\Results_75524\Cell_i54801_x94_y227_DevelopedHighIntensity_54801.csv']

column_name = 'Biomass(gN/m2)'

time_df = pd.read_csv(initial_file_paths[0], usecols=['Year', 'Jday'])
time_df['Time'] = pd.to_datetime(time_df['Year'].astype(str)) + pd.to_timedelta(time_df['Jday'] - 1, unit='D')

initial_df = pd.DataFrame(time_df['Time'])
reduced_uptake_df = pd.DataFrame(time_df['Time'])

for file_path in initial_file_paths:
    name_parts = file_path.rsplit('_', 2)
    name = '_'.join([name_parts[1], name_parts[2]])
    df = pd.read_csv(file_path, usecols=[column_name])
    df = df.rename(columns={column_name: name})
    initial_df[name] = df[name]

for file_path in reduced_uptake_file_paths:
    name_parts = file_path.rsplit('_', 2)
    name = '_'.join([name_parts[1], name_parts[2]])
    df = pd.read_csv(file_path, usecols=[column_name])
    df = df.rename(columns={column_name: name})
    reduced_uptake_df[name] = df[name]


ax = reduced_uptake_df.set_index('Time').plot(ylabel='Biomass values (gN/m2)')
plt.title('Reduced Uptake Michaelis-Menten parameters')
plt.legend()
plt.show()

# Select the columns to plot
columns_to_plot = initial_df.columns[1:]

# Create subplots
fig, axes = plt.subplots(nrows=len(columns_to_plot), ncols=1, figsize=(10, 15), sharex=True)

# Plot each column
for ax, column in zip(axes, columns_to_plot):
    ax.plot(initial_df.index, initial_df[column], label=f'{column} (Initial)', alpha=0.7)
    ax.plot(reduced_uptake_df.index, reduced_uptake_df[column], label=f'{column} (Reduced Uptake)', alpha=0.7, linestyle='--')
    
    # Set labels and title
    ax.set_title(f'Comparison of {column}')
    ax.set_ylabel('Biomass (gN/m2)')
    ax.legend()
    ax.grid(True)

# Set shared x-axis label
plt.xlabel('Time')
plt.tight_layout()
plt.show()
