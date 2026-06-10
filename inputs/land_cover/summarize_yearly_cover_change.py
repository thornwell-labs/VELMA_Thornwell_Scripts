"""
Converts VELMA CoverCounts.csv outputs into yearly land cover change tables.
Reads per-step cover counts from one or more simulation result folders,
collapses them to one row per year, and writes a Yearly_Cover_Change CSV
for each input.
"""

import pandas as pd

in_paths = [
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_119917\CoverCounts.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_122721\CoverCounts.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_168806\CoverCounts.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_203672\CoverCounts.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_219017\CoverCounts.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_392877\CoverCounts.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_424498\CoverCounts.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_560087\CoverCounts.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_308243\CoverCounts.csv"
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_333762\CoverCounts.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_452885\CoverCounts.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_387038\CoverCounts.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_362794\CoverCounts.csv"
    r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_475720\CoverCounts.csv",
    r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_308243\CoverCounts.csv",
    r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_404119\CoverCounts.csv",
    r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_489285\CoverCounts.csv"
            ]
out_paths = [
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_119917\Yearly_Cover_Change.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_122721\Yearly_Cover_Change.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_168806\Yearly_Cover_Change.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_203672\Yearly_Cover_Change.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_219017\Yearly_Cover_Change.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_392877\Yearly_Cover_Change.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_424498\Yearly_Cover_Change.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_560087\Yearly_Cover_Change.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_308243\Yearly_Cover_Change.csv"
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_333762\Yearly_Cover_Change_333762.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_452885\Yearly_Cover_Change_452885.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_387038\Yearly_Cover_Change_387038.csv",
    # r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_362794\Yearly_Cover_Change_362794.csv"
    r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_475720\Yearly_Cover_Change_475720.csv",
    r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_308243\Yearly_Cover_Change_308243.csv",
    r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_404119\Yearly_Cover_Change_404119.csv",
    r"path\to\VELMA_Watersheds\Samish\Results\MULTI_WA_Samish30m_PSIMF_Penumbra_RiparianBufferProtection\Results_489285\Yearly_Cover_Change_489285.csv"
             ]

column_names = [
    'Step', 'Alder5Percent_5', 'Alder17Percent_6', 'Alder37Percent_7', 'Grassland_71', 'Alder62Percent_8', 'Alder88Percent_9', 'EvergreenForest_42', 'Water_11',
    'MixedForest_43', 'SnowIce_12', 'Pasture_81', 'Cultivated_82', 'ShrubScrub_52', 'DevelopedOpenSpace_21', 'DevelopedLowIntensity_22', 'DevelopedMediumIntensity_23',
    'DevelopedHighIntensity_24', 'Wetlands_90', 'BareLand_31'
]

start_year = 2029

for in_path, out_path in zip(in_paths, out_paths):
    df = pd.read_csv(in_path, header=None, names=column_names)

    df['Step'] = pd.to_numeric(df['Step'], errors='coerce')
    df = df.dropna(subset=['Step']).copy()
    df['Step'] = df['Step'].astype(int)

    cover_cols = [col for col in column_names if col != 'Step']

    for col in cover_cols:
        df[col] = df[col].astype(str).str.split('#').str[1].astype(int)

    df['Date'] = pd.date_range(start='2029-01-01', periods=len(df), freq='D')
    df['Year'] = df['Date'].dt.year
    
    step0 = df[df['Step'] == 0].iloc[0]
    total_cells = step0[cover_cols].sum()

    year_end_rows = (
        df.sort_values('Step')
          .groupby('Year', as_index=False)
          .tail(1)
          .copy()
    )

    out_rows = []
    for _, row in year_end_rows.iterrows():
        year = int(row['Year'])
        pct_cover = (row[cover_cols] / total_cells) * 100
        pct_cover['Year'] = year
        out_rows.append(pct_cover)

    out_df = pd.DataFrame(out_rows)
    out_df = out_df[['Year'] + cover_cols]
    out_df.to_csv(out_path, index=False)
