# Downloads daily USGS streamflow (parameter 00060) for a gage over a date
# range using the dataRetrieval package and writes it to a CSV in the VELMA
# observed-data folder. R companion to retrieve_usgs_data.py.

# clean workspace
rm(list = ls())

# Start and end dates of desired data
Start <- "1981-01-01"
End <- "2021-12-31"

# Retrieve data retrieval package and make sure it's installed
packages <- c("dataRetrieval")
if (length(setdiff(packages, rownames(installed.packages()))) > 0) {
  install.packages(setdiff(packages, rownames(installed.packages())))  
}
lapply(packages, require, character.only = T)

# Specify the gage number and retrieve daily data at the specified date range
gage <- 12200500
daily <- readNWISdv(gage, parameterCd="00060", startDate=Start, endDate = End)
daily <- daily[,c(3, 4)]
colnames(daily) <- c("Date", "Q_cfs")

# Set output file path
output_folder <- "path/to/VELMA_Watersheds/Skagit/Data_Inputs30m/m_7_Observed"
output_file <- paste0(output_folder, "/gage_", gage, "_", Start, "_to_", End, ".csv")

# Write to CSV
write.csv(daily, file = output_file, row.names = FALSE)
