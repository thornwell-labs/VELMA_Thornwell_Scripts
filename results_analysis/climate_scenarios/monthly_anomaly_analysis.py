"""
Computes monthly anomalies for each hydrologic variable and decade relative to
its annual mean, from the seasonal trend CSVs in the PSIMF hydro analysis,
writing monthly average and anomaly tables for trend visualization.
"""

import pandas as pd
import os
import matplotlib.pyplot as plt

analysis_folder = 'path/to/PSIMF Management/Proof_of_Concept_QC/Hydro_Analysis'

for file in os.listdir(analysis_folder):
    if file.endswith('.csv') and 'monthly_anomalies' not in file:
        df = pd.read_csv(os.path.join(analysis_folder, file))
        columns = df.columns[1:]  # Grab all columns but the first (Julian_Day)
        df['Date'] = pd.to_datetime(df['Julian_Day'], format='%j')
        df['Month'] = df['Date'].dt.month
        months = sorted(df['Month'].dropna().unique())  # Get list of unique months
        
        # Instantiate a dataframe named out_df with column Month and list of unique months
        out_df = pd.DataFrame({'Month': months})
        
        # Compute the monthly anomalies for each decade
        for column in columns:
            yearly_average = df[column].mean()
            monthly_anomalies = []
            anomaly_col_name = f'{column}s Monthly Anomaly'
            monthly_averages = []
            average_col_name = f'{column}s Monthly Average'
            
            for month in months:
                monthly_average = df.loc[df['Month'] == month, column].mean()
                monthly_averages.append(monthly_average)
                monthly_anomaly = monthly_average / yearly_average
                monthly_anomalies.append(monthly_anomaly)
                
            out_df[anomaly_col_name] = monthly_anomalies
            out_df[average_col_name] = monthly_averages
            
        plt.figure(figsize=(10, 6))
        for column in columns:
            average_col_name = f'{column}s Monthly Average'
            plt.plot(out_df['Month'], out_df[average_col_name])
        plt.xlabel('Month')
        plt.ylabel('Monthly Average')
        plt.title(f'Monthly Averages — {file.replace(".csv", "")}')
        plt.xticks(range(1, 13))
        plt.grid(True, alpha=0.3)
        plt.legend()

        plot_file = os.path.join(
            analysis_folder,
            file.replace('.csv', '_monthly_averages.png')
        )
        plt.tight_layout()
        plt.savefig(plot_file)
        plt.show()
        
        out_file = os.path.join(
            analysis_folder,
            file.replace('.csv', '_monthly_anomalies.csv')
        )
        out_df.to_csv(out_file, index=False)
