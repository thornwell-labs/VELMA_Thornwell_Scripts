# VELMA Watershed Modeling Scripts

A collection of Python (and one R) utilities developed to support watershed
modeling with [**VELMA**](https://www.epa.gov/water-research/visualizing-ecosystem-land-management-assessments-velma-model)
(Visualizing Ecosystem Land Management Assessments), EPA's spatially
distributed eco-hydrological model. The scripts cover 
preparing model inputs, running simulations, calibrating and validating against
observed data, analyzing outputs, and handing results off to other modeling
teams.

Much of this work was performed for the Puget Sound climate-scenario modeling
effort referred to throughout the code as **PSIMF**.

## Conventions

- Most scripts are **single-purpose and configured by editing the variables at
  the top of the file** (input paths, watershed name, year ranges) rather than
  via command-line arguments.
- Grids are ESRI ASCII (`.asc`) or GeoTIFF (`.tif`); the working projection is
  NAD83 / UTM Zone 10N (EPSG:26910).
- "DailyResults.csv", "cell data writer" (`dlnWriter`), "Spatial_*" rasters,
  and "ReachSummary.csv" referenced throughout are standard VELMA outputs.

## External model acronyms

| Acronym | Model |
|---|---|
| **SSM** | Salish Sea Model |
| **WASP** | Water Quality Analysis Simulation Program |
| **SPARROW** | USGS SPAtially Referenced Regression On Watershed attributes |
| **QNM** | Qualitative Network Model |

---

## Repository layout

```
inputs/                     Prepare VELMA input grids and drivers
  soil/                     SOLUS soil processing, C/N, restrictive depth
  land_cover/               NLCD/LEMMA land cover prep and QC
  climate/                  Precipitation/temperature drivers
  chemistry_pools/          Biomass/nitrogen pool initialization
point_source_nitrogen/      Wastewater, hatchery, and septic nitrogen
  generation/               Build monthly loads / disturbance grids
  forecasting/              Project loads into the future
  analysis/                 Inspect and summarize point-source loads
model_runs/                 Launch runs; set up outlets and cell writers
calibration_validation/     Compare simulations to observed data
results_analysis/           Post-process simulation output
  hydrology/
  nitrogen/
  climate_scenarios/        PSIMF decadal/seasonal trend analysis
external_models/            Hand-offs to other modeling teams
  ssm/   wasp/   sparrow/   qnm/
visualization/              General-purpose plotting and figures
utilities/                  Raster helpers and miscellaneous tools
```

---

## inputs/soil/
SOLUS soil-property download through to VELMA-ready soil grids.

| File | Description |
|---|---|
| `download_solus_data.py` | Downloads SOLUS100 soil property rasters from the public cloud bucket. |
| `solus_interpolator.py` | Interpolates SOLUS properties from published depths to VELMA soil-layer depths. |
| `soc_unit_conversion.py` | Converts percent-SOC rasters to g/m² using bulk density, layer thickness, and rock fraction. |
| `merge_soc_depth_layers.py` | Merges shallow/medium/deep restrictive-depth SOC rasters into one seamless layer. |
| `mask_soc_by_depth_cluster.py` | Masks an interpolated SOC raster to a single restrictive-depth cluster. |
| `restdepth_k_means.py` | Clusters a restrictive-depth raster into groups via k-means. |
| `c_n_ratio_classification.py` | Builds a C/N ratio raster from NLCD land cover classes. |
| `c_to_n_conversion.py` | Converts soil organic carbon rasters (g/m²) to nitrogen using a C/N ratio raster. |
| `generate_humus_n_reduction_raster.py` | Creates a humus-nitrogen reduction-fraction raster from land cover classes. |
| `soil_classifier.py` | Builds a soil-type ID map from clustered restrictive depth and C/N ratio. |
| `count_soil_type_cells.py` | Counts raster cells belonging to each soil type in a soil-types map. |
| `solus_to_velma_grid.py` | Resamples a SOLUS raster to match a watershed DEM grid (.asc output). |
| `solus_to_velma_grid_soiltype.py` | Same as above for categorical soil-type IDs (nearest-neighbor). |
| `multiply_asc_by_constant.py` | Multiplies an .asc grid by a constant (e.g. halving humus nitrogen). |
| `multiply_asc_files.py` | Multiplies two .asc grids cell-by-cell (e.g. apply reduction fractions). |
| `pervious_fraction_calculator.py` | Converts a land cover grid to percent-pervious for `setPermeabilityFraction`. |

## inputs/land_cover/

| File | Description |
|---|---|
| `add_land_cover.py` | Adds an NLCD land cover class (e.g. pasture) into an existing VELMA land cover .asc. |
| `land_cover_resampler.py` | Downsamples a land cover grid by majority rule while preserving class proportions. |
| `embed_land_cover_names_vrt.py` | Builds a GDAL VRT that embeds human-readable land cover class names. |
| `land_cover_parameter_extractor.py` | Extracts per-cover parameters from a VELMA configuration XML to CSV. |
| `summarize_yearly_cover_change.py` | Converts VELMA `CoverCounts.csv` into yearly land cover change tables. |
| `lccm_checker.py` | QC of Land Cover Change Model files: plots percent of the map changed per year. |

## inputs/climate/

| File | Description |
|---|---|
| `calculate_average_daily_precip.py` | Watershed-average daily precipitation from spatial weather driver files. |
| `calculate_average_daily_precip_multicore.py` | Parallel version processing multiple watersheds at once. |
| `calculate_average_daily_temp.py` | Watershed-average daily air temperature from spatial weather driver files. |
| `snow_to_precip_analysis.py` | Snow-to-total-precipitation ratio across decadal PSIMF runs. |

## inputs/chemistry_pools/
Initialize VELMA biomass and nutrient pools.

| File | Description |
|---|---|
| `biomass_initialization_update.py` | Overwrites biomass values in chemistry pool initialization rasters by land cover class. |
| `update_chemistry_pool_initialization.py` | Overwrites nitrate/ammonium/biomass/detritus initialization rasters by land cover class. |
| `rename_chem_pools_1995.py` | Renames 1995 end-state spatial data writers to the chemistry pool filenames VELMA expects as inputs. |
| `rename_chem_pools_2010.py` | Same as above for the 2010 end-state. |

---

## point_source_nitrogen/generation/

| File | Description |
|---|---|
| `wwtp_nitrogen_generator.py` | Monthly nitrogen loads (NH4/NO3/DON) for wastewater treatment plants from Ecology nutrient data. |
| `hatchery_nitrogen_generator.py` | Monthly nitrogen loads for fish hatcheries using assumed nitrogen speciation. |
| `public_septic_disturbance_generator.py` | Builds septic NH4 and water disturbance .asc grids for a watershed. |
| `point_source_nitrogen_handler.py` | Classifies facilities and dispatches to the matching load generator. |

## point_source_nitrogen/forecasting/

| File | Description |
|---|---|
| `forecast_future_wwtp_nitrogen.py` | Projects WWTP nitrogen loads to 2099 using county population growth rates. |
| `add_future_point_source_nitrogen.py` | Adds projected point-source loads to VELMA future-scenario results. |
| `plot_facility_nitrogen_history.py` | Plots historical facility loads to inform forecasting. |

## point_source_nitrogen/analysis/

| File | Description |
|---|---|
| `point_source_nitrogen_analysis.py` | Combines runs with and without point-source nitrogen to quantify its contribution. |
| `monthly_tn_calculator.py` | Average monthly total-nitrogen load per facility in the PSIMF list. |
| `tn_contributor_bar_chart.py` | Bar charts of total-nitrogen load by facility type per watershed. |
| `plot_facility_nitrogen_timeseries.py` | Plots one column of the nutrient dataset over time for a facility. |
| `missing_data_checker.py` | Reports gaps in the point-source nutrient dataset. |

---

## model_runs/
Launch simulations and set up run geometry.

| File | Description |
|---|---|
| `run_velma_loop.py` | Runs a sequence of VELMA simulations from the command line. |
| `list_outlet_result_folders.py` | Lists all outlet result folders from a parallel run. |
| `filter_failed_outlets.py` | Filters failed outlets out of an outlet list. |
| `add_to_outlet_shapefile.py` | Merges tabular data (e.g. flow fractions) into an outlet shapefile. |
| `add_soil_names.py` | Joins SSURGO soil names into a soil polygon shapefile. |
| `watershed_areas.py` | Calculates the area (km²) of each watershed shapefile in a folder. |
| `lookup_cell_writer_land_cover.py` | Looks up the land cover code for each cell data writer location. |
| `cell_dwriter_visualizer.py` | Plots a cell data writer variable across two simulation runs. |
| `water_balance_cell_dwriter.py` | Visualizes the water balance at a single cell over selected years. |

---

## calibration_validation/
Compare simulations against observed data and prepare observed datasets.

| File | Description |
|---|---|
| `nse_calculator.py` | Overall Nash-Sutcliffe Efficiency vs a VELMA-format observed file. |
| `nse_calculator_obs.py` | Yearly NSE vs a real observed file. |
| `nse_calculator_by_year.py` | Yearly NSE between two result files (e.g. full vs resampled grid). |
| `seasonal_nse_calculator.py` | Seasonal NSE vs observed. |
| `calculate_summer_nse.py` | Summer-only NSE vs observed USGS streamflow. |
| `r2_calculator.py` | Overall coefficient of determination (R²) vs observed. |
| `r2_calculator_by_year.py` | Yearly R² vs observed. |
| `mape_calculator.py` | Mean absolute percentage error vs observed. |
| `mean_error_calculator.py` | Mean error (simulated − observed), converted to kg/day. |
| `soar_calculator.py` | Annual and summer simulated-to-observed runoff ratio (SOAR). |
| `calculate_summer_soar.py` | Summer-only simulated-to-observed runoff ratio. |
| `compare_usgs_temperature.py` | Simulated vs observed water temperature at multiple USGS gages. |
| `compare_usgs_temperature_single.py` | Single-gage version of the above. |
| `temperature_comparison.py` | Simulated vs observed temperature with a seasonal breakdown. |
| `snotel_comparison.py` | Simulated snow depth vs observed SNOTEL snow water equivalent. |
| `biomass_validation.py` | Validates simulated biomass against an observed biomass raster and drivers. |
| `pearson_correlation_with_facc.py` | Correlates flow accumulation with chemistry pool rasters. |
| `retrieve_usgs_data.py` | Downloads USGS NWIS data (e.g. temperature) for a list of gages. |
| `Retrieve_USGS_Flows.R` | Downloads USGS daily streamflow (R companion to the above). |
| `ecology_create_obs_file.py` | Builds VELMA-format observed files from WA Ecology data with unit conversion. |
| `merge_ecology_nutrient_samples.py` | Merges Ecology ammonia/nitrate samples into a comparison table. |
| `inventory_ecology_locations.py` | Inventories Ecology monitoring locations (period of record, flow availability). |
| `DOE_data_explorer.py` | Extracts unique Ecology monitoring locations for parameters of interest. |
| `DOE_data_organizer.py` | Splits the Ecology dataset into one CSV per parameter. |

---

## results_analysis/hydrology/

| File | Description |
|---|---|
| `hydrologic_results_compiler.py` | Compiles decadal PSIMF runs into one continuous dataset with seasonal totals. |
| `water_balance_dailyresults.py` | Watershed-scale water balance from a DailyResults file. |
| `monthly_means.py` | Monthly mean observed vs simulated flow (mm → cfs). |
| `analyze_average_precip_change.py` | Decadal change in watershed-average precipitation. |
| `flow_weighted_temp_calculator.py` | Flow-weighted water temperature by marine basin. |
| `compare_groundwater_to_baseflow.py` | Compares VELMA groundwater-box behavior to a baseflow-separation model. |
| `observed_runoff_stats.py` | Quick statistics and plot for an observed streamflow file. |
| `plot_pool_percent_change.py` | Plots percent change in chemistry pools by cover and soil type. |
| `flow_results_comparison.py` | Compares simulated flow across runs vs observed. **Note: incomplete/broken as written.** |

## results_analysis/nitrogen/

| File | Description |
|---|---|
| `nitrogen_tracker.py` | Yearly nitrogen budget (pool change + losses) across source-elimination scenarios. |
| `humus_nitrogen_calculator.py` | Yearly average humus nitrogen across source-elimination scenarios. |
| `compute_annual_pool_change.py` | Annual percent change in carbon/nitrogen pools across watersheds. |
| `summarize_annual_pct_change.py` | Plots the annual percent-change tables, one figure per pool. |
| `compare_nitrogen_related_variables.py` | Nitrogen variables by cover type across two scenarios. |
| `seasonal_nitrogen_load_calculator.py` | Seasonal total-nitrogen loads (kg) using SPARROW season definitions. |

## results_analysis/climate_scenarios/
PSIMF decadal and seasonal trend analysis.

| File | Description |
|---|---|
| `total_decadal_trend.py` | Region-wide total decadal trend of a variable across watersheds. |
| `decadal_trend_by_watershed.py` | Per-watershed decadal totals and percent differences. |
| `decadal_marine_basin_trend.py` | Decadal load trends aggregated by marine basin. |
| `decadal_monthly_trend.py` | Monthly-mean trends by decade across watersheds. |
| `decadal_seasonal_trend.py` | Seasonal (day-of-year) trends by decade. |
| `decadal_seasonal_trend_precip.py` | Precipitation-input variant of the seasonal trend. |
| `hydro_variable_trend.py` | Century-scale trends of hydrologic variables across watersheds. |
| `hydro_variable_trend_monthly_average.py` | Monthly-averaged variant of the above. |
| `annual_change_hydrologic_analysis.py` | Yearly runoff change vs rainfall, snowmelt, ET, and soil saturation. |
| `annual_change_hydrologic_correlation_analysis.py` | Correlates runoff change with drivers and developed-cover change. |
| `hydrologic_correlation_analysis.py` | Single-watershed correlation of hydrology with land cover change. |
| `hierarchical_regression.py` | Hierarchical regression of runoff on drivers, by season. |
| `k_means_runoff_drivers.py` | Clusters watersheds by their runoff-driver correlation signatures. |
| `monthly_anomaly_analysis.py` | Monthly anomalies per variable and decade. |
| `PSIMF_hydro_pattern_analysis.py` | Seasonal hydrologic patterns averaged across watersheds. |
| `percent_lccm_by_year.py` | Per-watershed yearly developed/forested/agricultural cover proportions. |
| `penumbra_coverage_generator.py` | Generates a full-coverage (all-ones) .asc penumbra mask input. |

---

## external_models/ssm/
Salish Sea Model hand-offs and SSM-format processing.

| File | Description |
|---|---|
| `ssm_data_generator.py` | Converts VELMA outlet results to SSM CSV format, including water temperature. |
| `ssm_full_result_generator.py` | Concatenates per-decade SSM files into one full-period file per watershed. |
| `ssm_result_visualizer.py` | Plots SSM results per watershed across baseline and future decades. |
| `ssm_runoff_analysis.py` | Annual runoff statistics per watershed from SSM files. |
| `ssm_file_comparison.py` | Overlays common columns from multiple SSM result CSVs. |
| `load_calculator.py` | Converts SSM concentrations (mg/L) to loads (kg/day) and flow-weighted temperature. |

## external_models/wasp/

| File | Description |
|---|---|
| `wasp_data_generator.py` | Compiles VELMA results into WASP inputs (per-COMID flow and nitrogen series). |

## external_models/sparrow/

| File | Description |
|---|---|
| `sparrow_data_extractor.py` | Extracts per-watershed total-nitrogen predictions from SPARROW output by COMID. |
| `sparrow_tn_comparison.py` | Compares VELMA total-nitrogen loads to SPARROW predictions. |

## external_models/qnm/

| File | Description |
|---|---|
| `compute_qnm_annual_statistics.py` | Annual runoff and temperature statistics for the QNM team from SSM files. |

---

## visualization/
General-purpose plotting of model outputs and inputs.

| File | Description |
|---|---|
| `daily_visualizer.py` | Plots a variable over time from one or more results files (multiple scenarios). |
| `daily_visualizer_single.py` | Single-file version. |
| `daily_visualizer_by_cover.py` | One line per land cover type. |
| `daily_visualizer_by_soil.py` | One line per soil type. |
| `loss_visualizer.py` | Nitrogen/carbon loss variables across source-elimination scenarios. |
| `nse_visualizer.py` | Observed vs simulated runoff with per-year NSE labels. |
| `runoff_visualizer.py` | Observed vs simulated runoff across scenarios with NSE labels. |
| `runoff_vs_precip_plots.py` | Day-of-year runoff by decade alongside precipitation. |
| `precip_vs_runoff_charts.py` | Day-of-year precipitation vs runoff on a dual axis. |
| `hydro_variable_by_jday_plots.py` | Each hydrologic variable by day of year, one line per decade. |
| `seasonal_hydrologic_analysis.py` | Seasonal hydrologic correlation analysis for all watersheds. |
| `seasonal_hydrologic_analysis_no_sum.py` | Single-watershed, non-summed variant. |
| `annual_results_delta_figure.py` | Annual change in major carbon/nitrogen pools from AnnualResults. |
| `humus_figure_generator.py` | Humus carbon pools over time across decadal runs. |
| `npp_figure_generator.py` | Annual net primary productivity by land cover group. |
| `visualize_total_npp.py` | Total annual NPP summed across cover types. |
| `age_biomass_chart.py` | Conifer biomass vs stand age from co-located rasters. |
| `summarize_pools_by_land_cover.py` | Summarizes chemistry pool rasters by land cover class. |
| `analyze_spatial_pool_differences.py` | Mean percent difference in each chemistry pool by land cover, between two pool sets. |
| `histogram_generator.py` | Land cover / soil type distribution within a watershed (pie/histogram). |
| `box_and_whisker_plots.py` | Box-and-whisker summary of the penumbra (riparian shading) analysis. |
| `ecology_figure_generator.py` | Day-of-year simulated envelope with observed Ecology points overlaid. |
| `cover_parameter_comparison_plots.py` | Cover-specific parameter changes across model versions. |
| `parameter_comparison_plots.py` | A single parameter across model versions (bar chart). |
| `qc_figure_generator.py` | Batch QC figures of chemistry variables grouped by cover. |
| `qc_report_generator.py` | Bundles a folder of PNG figures into a multi-page PDF report. |

---

## utilities/
Reusable raster helpers and miscellaneous tools.

| File | Description |
|---|---|
| `resample_raster.py` | Reusable helper: resamples a raster to match a reference grid (imported by other scripts). |
| `merge_rasters.py` | Mosaics all .asc grids in a directory via `rasterio.merge`. |
| `mosaic_asc_grids.py` | Stitches all .asc grids in a directory into one grid by stacking. |
| `replace_invalid_soil_codes.py` | Replaces invalid soil-type codes in .asc grids with a default value. |
| `raster_reprojection.py` | Reprojects/resamples a source raster to match a reference raster's grid (configured to align a C/N ratio raster to a humus grid). |
| `asc_statistics.py` | Min/max/mean for every .asc in a directory, written to CSV. |
| `asc_index_converter.py` | Converts a linear cell index to (row, column) using a raster's width. |
| `build_outlet_extraction_expression.py` | Builds a QGIS raster-calculator expression to mask outlet cells, written to a file. |
| `infinity_finder.py` | Scans result folders for `Infinity` values in DailyResults (diagnostic for unstable runs). |
| `xml_comparison.py` | Reports parameter differences between two VELMA configuration XMLs. |
| `FIA_processing.py` | Processes USFS Forest Inventory and Analysis data into per-plot aboveground carbon. |
