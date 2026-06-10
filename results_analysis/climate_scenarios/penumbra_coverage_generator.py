"""
Generates a uniform ESRI ASCII grid (.asc) filled entirely with the value 1,
given grid dimensions and georeferencing. Used to create a full-coverage
'penumbra' mask input for VELMA scenario runs.
"""


def create_asc(
    output_path,
    ncols,
    nrows,
    xllcorner,
    yllcorner,
    cellsize,
    nodata_value=-9999
):
    with open(output_path, "w") as f:
        # Write header
        f.write(f"ncols         {ncols}\n")
        f.write(f"nrows         {nrows}\n")
        f.write(f"xllcorner     {xllcorner}\n")
        f.write(f"yllcorner     {yllcorner}\n")
        f.write(f"cellsize      {cellsize}\n")
        f.write(f"NODATA_value  {nodata_value}\n")
        
        # Write grid values
        row_values = " ".join(["1"] * ncols)
        for _ in range(nrows):
            f.write(row_values + "\n")


# Example usage
create_asc(
    output_path=r"path\to\VELMA_Watersheds\Samish\Data_Inputs30m\m_5_Coverage\Samish_Penumbra_Coverage.asc",
    ncols=968,
    nrows=870,
    xllcorner=534873.8171,
    yllcorner=5370783.0198,
    cellsize=30.0
)
