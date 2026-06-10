"""
Downloads USGS NWIS data (e.g. water temperature) for a list of gage sites
using the dataretrieval package. Tries daily values first and falls back to
instantaneous values, saving raw CSVs to the observed-data folder.
See Retrieve_USGS_Flows.R for the streamflow equivalent in R.
"""

import dataretrieval.nwis as nwis
import pandas as pd

# Example parameters
sites = ['12056500', '12058790', '12058800', '12059500', '12060500', '12061250', '12061500']          # USGS site number
start_date = '1990-01-01'   # Start of period
end_date = '2021-12-31'     # End of period
parameter_code = '00010'    # Water temperature
out_folder = 'path/to/VELMA_Watersheds/Skokomish/Data_Inputs30m/m_7_Observed'

for site in sites:
    # Try to download raw data using daily values
    try:
        df = nwis.get_record(
            sites=site,
            service='dv',
            start=start_date,
            end=end_date,
            parameterCd=parameter_code
        )
    except Exception as e:
        print(f"Error retrieving dv data for site {site}: {e}")
        df = None

    # If that didn't work, try to download raw data using instantaneous values
    if df.empty:
        print(f'No data found for site {site}. Attempting to download instantaneous values.')
        try:
            df = nwis.get_record(
            sites=site,
            service='iv',
            start=start_date,
            end=end_date,
            parameterCd=parameter_code
        )
        except Exception as e:
            print(f"Error retrieving iv data for site {site}: {e}")
            df = None
    
    # Save raw data to CSV
    if df is not None and not df.empty:
        df.index = pd.to_datetime(df.index)
        df.index = df.index.tz_localize(None)
        df = df['00010_Mean']

        # --- Ensure full date range ---
        all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        df = df.reindex(all_dates)

        # --- Rename index to 'date' for clarity ---
        out_path = f'{out_folder}/USGS_{site}_Temperature_Raw.csv'
        df.to_csv(out_path)
        print(f"Raw temperature data saved to {out_path}")
    else:
        print(f"No data returned for site {site}")
