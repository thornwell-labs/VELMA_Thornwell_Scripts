"""
Runs a hierarchical (stepwise-by-block) linear regression of runoff on
rainfall, snowmelt, evapotranspiration, and soil saturation by season,
quantifying the incremental variance each driver explains in the PSIMF
full-period hydro results.
"""

import pandas as pd
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.anova import anova_lm

results_path = "path/to/VELMA_Watersheds/Big_Beef/Results/Big_Beef_PSIMF_full_hydro_results.csv"
out_path = "path/to/VELMA_Watersheds/Big_Beef/Analysis/Big_Beef_runoff_hierarchical_regression.csv"

dependent_var = 'Runoff_All(mm_day)_Delineated_Average'

season_dict = {
    'Spring': range(91, 150),   # Apr–Jun
    'Summer': range(150, 258),  # Jul–Sep
    'Fall': range(258, 367),    # Oct–Dec
    'Winter': list(range(1, 91))  # Jan–Mar
}

def assign_season(jday):
    for season, days in season_dict.items():
        if jday in days:
            return season

hierarchy = [
    'Rain(mm_day)_Delineated_Average',
    'Snow_Melt(mm_day)_Delineated_Average',
    'ET(mm_day)_Delineated_Average',
    'Soil_Saturation_Fraction_Delineated_Average_Layer_1'
]

df = pd.read_csv(results_path)

# Filter to years past 2010
df = df[df['Year'] > 2010]

# Assign season
df['Season'] = df['Day'].apply(assign_season)

all_results = []

# -------------------------------
# Seasonal hierarchical regression
# -------------------------------
for season in season_dict.keys():

    print(f"\n{'='*60}")
    print(f"Hierarchical regression for {season}")
    print(f"{'='*60}")

    season_df = df[df['Season'] == season].dropna(
        subset=[dependent_var] + hierarchy
    )

    # Skip if too few observations
    if len(season_df) < 20:
        print(f"Skipping {season}: insufficient data")
        continue

    # Standardize WITHIN season
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(
        season_df[[dependent_var] + hierarchy]
    )

    scaled_df = pd.DataFrame(
        scaled_data,
        columns=[dependent_var] + hierarchy,
        index=season_df.index
    )

    X_prev = pd.DataFrame(index=scaled_df.index)
    R2_prev = 0.0
    models = []

    for step, var in enumerate(hierarchy, start=1):

        X_current = pd.concat([X_prev, scaled_df[[var]]], axis=1)
        X_current = sm.add_constant(X_current)

        model = sm.OLS(scaled_df[dependent_var], X_current).fit()
        models.append(model)

        R2_current = model.rsquared
        delta_R2 = R2_current - R2_prev

        all_results.append({
            'Season': season,
            'Step': step,
            'Variable_Added': var,
            'R2': R2_current,
            'Delta_R2': delta_R2,
            'Std_Coefficient': model.params[var],
            'p_value': model.pvalues[var]
        })

        print(f"\nStep {step}: {var}")
        print(f"R² = {R2_current:.3f}")
        print(f"ΔR² = {delta_R2:.3f}")
        print(f"β = {model.params[var]:.3f} (p = {model.pvalues[var]:.3g})")

        X_prev = X_current.drop(columns='const')
        R2_prev = R2_current

    # Nested F-tests
    for i in range(1, len(models)):
        ftest = anova_lm(models[i-1], models[i])
        print(f"\nAdded {hierarchy[i]}:")
        print(ftest)

# Save all seasonal results
results_df = pd.DataFrame(all_results)
results_df.to_csv(out_path, index=False)
