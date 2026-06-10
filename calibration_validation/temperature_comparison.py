"""
Compares VELMA-simulated water surface temperature to observed USGS gage
temperature with a seasonal breakdown (seasons defined to match SPARROW).
Reports R^2 and seasonal statistics and writes a comparison CSV per site.
"""

import pandas as pd
from sklearn.metrics import r2_score
import os

for site_no in ['12147500']:
    watershed = 'Snohomish'
    site = f'USGS {site_no}'
    model_run = 'Historical without Penumbra'
    out_file = f"path/to/VELMA_Watersheds/{watershed}/Analysis/Temp_Comparison_{site}.csv"
    
    # Single file definitions
    observed_file = fr"path\to\VELMA_Watersheds\Snohomish\Data_Inputs30m\m_7_Observed\USGS_Temperature\USGS_{site_no}.csv"
    simulated_file = r"path\to\VELMA_Watersheds\Snohomish\Results\MULTI_WA_Snohomish30m_Historical_resampled_3\Results_743663\Cell_i743663_x423_y680_dlnWriter.csv"
    
    # Loop definitions
    # observed_file = f"path/to/VELMA_Watersheds/{watershed}/Data_Inputs30m/m_7_Observed/USGS_{site_no}_Temperature_Raw.csv"
    # folder = r"path\to\VELMA_Watersheds\Skagit\Results\MULTI_WA_Skagit30m_Historical_resampled_3"
    # for file in os.listdir(folder):
    #     if site_no in file:
    #         simulated_file = os.path.join(folder, file)
            
# ------------------------------------------------------------------------------------------ #    

    # This seasonal definition matches the SPARROW season definition
    season_dict = {
        '1': range(91, 181+1),  # Spring: April - June
        '2': range(182, 273+1),  # Summer: July - September
        '3': range(274, 365+1),  # Fall: October - December
        '4': range(1, 90+1)  # Winter: January - March
    }

    def jday_to_season(jday):
        for s, days in season_dict.items():
            if jday in days:
                return s
        return None

    obs = pd.read_csv(observed_file, parse_dates=['Date'])
    obs['Year'] = obs['Date'].dt.year
    obs['Jday'] = obs['Date'].dt.dayofyear
    obs['Season'] = obs['Jday'].apply(jday_to_season)

    # Obtain the years that have valid observed data
    valid_years = (
        obs.dropna(subset=['Mean Temp'])
        .groupby('Year')['Mean Temp']
        .count()
    )
    valid_years = valid_years[valid_years > 0].index.tolist()

    # Filter observed data to those valid years
    obs = obs[obs['Year'].isin(valid_years)].copy()

    # Read in simulated data
    sim = pd.read_csv(simulated_file, usecols=['Year', 'Jday', 'Water_Surface_Temperature(degrees_C)'])

    # Add Date column
    sim['Date'] = pd.to_datetime(
        sim['Year'].astype(int).astype(str), format='%Y'  # base at Jan 1
    ) + pd.to_timedelta(sim['Jday'] - 1, unit='D')

    # Add season column
    sim['Season'] = sim['Jday'].apply(jday_to_season)

    # Filter simulated data to valid years
    sim = sim[sim['Year'].isin(valid_years)].copy()

    # Merge on date to keep only days that have observed data
    merged = pd.merge(
        obs[['Date', 'Year', 'Jday', 'Season', 'Mean Temp']],
        sim[['Date', 'Year', 'Jday', 'Season', 'Water_Surface_Temperature(degrees_C)']],
        on='Date',
        how='inner',
        suffixes=('_obs', '_sim')
    )

    # Drop rows with missing temps (in case)
    merged = merged.dropna(subset=['Mean Temp', 'Water_Surface_Temperature(degrees_C)'])

    # Number of observed data points that have valid data
    n_points = len(merged)

    # R^2 between observed and simulated data points
    if n_points > 1:
        r2 = r2_score(
            merged['Mean Temp'],
            merged['Water_Surface_Temperature(degrees_C)']
        )
        r2 = round(r2, 2)
    else:
        r2 = float('nan')
        
    # Annual means
    annual_mean_obs = merged['Mean Temp'].mean()
    annual_mean_sim = merged['Water_Surface_Temperature(degrees_C)'].mean()
    annual_diff = annual_mean_sim - annual_mean_obs

    # Seasonal means and differences:
    # -Observed and simulated annual mean temp
    # -Observed and simulated mean temp for each season
    # -Difference (simulated - observed) mean temp, annual and for each season
    season_stats = {}
    for s in ['1', '2', '3', '4']:
        sub = merged[merged['Season_obs'] == s] if 'Season_obs' in merged.columns else merged[merged['Season_x'] == s]
        if len(sub) == 0:
            season_stats[s] = {
                'mean_obs': float('nan'),
                'mean_sim': float('nan'),
                'diff': float('nan')
            }
        else:
            mean_obs = round(sub['Mean Temp'].mean(), 2)
            mean_sim = round(sub['Water_Surface_Temperature(degrees_C)'].mean(), 2)
            season_stats[s] = {
                'mean_obs': mean_obs,
                'mean_sim': mean_sim,
                'diff': mean_sim - mean_obs
            }


    # Create row with these columns:
    # Watershed, site, model run, number data points, all other calculated values

    result = {
        'Watershed': watershed,
        'Site': site,
        'ModelRun': model_run,
        'n_points': n_points,
        'R2': r2,
        # 'Annual_Tavg_Obs': round(annual_mean_obs, 2),
        # 'Annual_Tavg_Sim': round(annual_mean_sim, 2),
        'Annual_Tavg_SimMinusObs_Diff': round(annual_diff, 2)
    }

    for s, name in {'1': 'Spring', '2': 'Summer', '3': 'Fall', '4': 'Winter'}.items():
        # result[f'{name}_Tavg_Obs'] = season_stats[s]['mean_obs']
        # result[f'{name}_Tavg_Sim'] = season_stats[s]['mean_sim']
        result[f'{name}_Tavg_SimMinusObs_Diff'] = season_stats[s]['diff']

    # Append row to out file
    out_df = pd.DataFrame([result])
    file_exists = os.path.isfile(out_file)
    out_df.to_csv(
        out_file,
        mode='a',          # append instead of overwrite
        index=False,
        header=not file_exists  # write header only if file doesn't exist
    )

    print(f"Saved metrics for {site} to: {out_file}")
