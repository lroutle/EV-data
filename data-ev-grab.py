# EV_vs_ICE_analysis.py
# Requires: pandas, numpy, matplotlib, seaborn, requests, eurostat (optional)
# pip install pandas numpy matplotlib seaborn requests pycountry eurostat

import os
import io
import requests
import zipfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style='whitegrid', context='talk')
outdir = 'ev_ice_charts'
os.makedirs(outdir, exist_ok=True)

# --- Helper functions
def save_csv(df, name):
    path = os.path.join(outdir, name)
    df.to_csv(path, index=False)
    print('Saved', path)

def stacked_chart(df, region, props, kind='absolute'):
    d = df[df.region == region].sort_values('year')
    years = d['year'].astype(int)
    colors = sns.color_palette('Set2', n_colors=len(props))
    fig, ax = plt.subplots(figsize=(12,6))
    bottom = np.zeros(len(d))
    for i,p in enumerate(props):
        vals = d[p].fillna(0).values
        if kind == 'share':
            total = d[props].sum(axis=1).replace(0, np.nan)
            vals = (d[p] / total).fillna(0).values
        ax.bar(years, vals, bottom=bottom, label=p, color=colors[i])
        bottom += vals
    ax.set_title(f'{region} annual new registrations by propulsion ({kind})')
    ax.set_xlabel('Year')
    ax.set_ylabel('Vehicles' if kind=='absolute' else 'Share')
    if kind=='share':
        ax.set_ylim(0,1)
    ax.legend(bbox_to_anchor=(1.02,1))
    plt.tight_layout()
    fname = f"{region}_stacked_{kind}.png"
    plt.savefig(os.path.join(outdir, fname), dpi=200)
    plt.close()

# --- 1) Pull Eurostat registrations by fuel type (public CSV)
# Eurostat bulk download endpoint for table: quadro "vehicle registrations by fuel"
# Prefer using eurostat package if installed; otherwise request CSV directly.
try:
    from eurostat import get_data_df
    # Example table code (may change); use "road_eqr_new" or fetch by name if available
    # Replace 'mot_park' or 'reg_passenger_cars' with the correct eurostat table id if needed
    print("Eurostat package available; will attempt to fetch known table ids.")
except Exception:
    pass

# Recommended direct Eurostat CSV fetch (replace TABLE_ID with correct id):
# Example:
# eurostat_url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/road_eqr_new?unit=NR&fuel=TOTAL&time=2015:2024&geo=EU27_2020"
# r = requests.get(eurostat_url)
# df_euro = pd.read_json(io.StringIO(r.text))  # parsing depends on endpoint format

# --- 2) UK: DfT / GOV.UK Vehicle licensing statistics
# GOV.UK provides XLSX/CSV files. Example download (manual step may be required if site layout changes).
uk_gov_csv = "https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/xxxx/vehicle-licensing-statistics.csv"
# Note: placeholder. If GOV.UK link requires navigation, download the CSV manually and place in ./data/uk_reg.csv

# --- 3) US: EPA / BTS data
# EPA Automotive Trends provides downloadable CSVs; BTS provides registration by fuel type.
# Example BTS CSV: https://www.bts.gov/sites/bts.dot.gov/files/2024-xx/vehicle_registrations_by_type.csv
# If direct link unavailable, download and place in ./data/us_reg.csv

# --- 4) Japan: JAMA / MLIT or JADA
# JAMA provides reports and possibly CSVs for registrations; if not, use CEIC / Statista (manual).
# Place file as ./data/japan_reg.csv

# --- 5) Global BEV/PHEV consolidated series (OWID / EVVolumes)
# Our World in Data maintains CSVs for EV sales: https://ourworldindata.org/grapher/ev-sales?tab=chart
# OWID direct CSV example:
owid_ev_url = "https://ourworldindata.org/grapher/ev-sales.csv"
r = requests.get(owid_ev_url)
if r.ok:
    ev_owid = pd.read_csv(io.StringIO(r.text))
    save_csv(ev_owid, 'owid_ev_sales_raw.csv')
else:
    print("Could not fetch OWID EV sales CSV; please download manually and place in data/")

# --- 6) Read local/manual files into harmonized dataframe
# Expected files: data/eurostat_reg.csv, data/uk_reg.csv, data/us_reg.csv, data/japan_reg.csv, data/global_ev.csv
data_dir = 'data'
files_expected = {
    'EU': os.path.join(data_dir, 'eurostat_reg.csv'),
    'UK': os.path.join(data_dir, 'uk_reg.csv'),
    'US': os.path.join(data_dir, 'us_reg.csv'),
    'Japan': os.path.join(data_dir, 'japan_reg.csv'),
    'Global_EV': os.path.join(data_dir, 'global_ev.csv'),
}

# Load and harmonize (the code below assumes each CSV has columns: year, fuel_type, count, but
# the exact parsing logic will be adapted to each source in the notebook)
def load_and_pivot(path, region_name):
    if not os.path.exists(path):
        print(f"Missing {path}. Please download the source and place it at this path.")
        return None
    df = pd.read_csv(path)
    # Normalize column names
    df.columns = [c.strip() for c in df.columns]
    # Heuristic mapping
    # Expect columns: year, fuel, value
    if 'year' not in df.columns:
        # try to detect year column
        for c in df.columns:
            if 'year' in c.lower():
                df = df.rename(columns={c:'year'})
                break
    if 'value' not in df.columns and 'count' in df.columns:
        df = df.rename(columns={'count':'value'})
    # Normalize fuel type names
    df['fuel_norm'] = df['fuel'].str.lower().str.replace('-', ' ').str.strip()
    # Map to the standard categories
    mapping = {
        'battery electric': 'BEV', 'battery-electric': 'BEV', 'electric': 'BEV',
        'plug-in hybrid': 'PHEV', 'plugin hybrid': 'PHEV', 'phev':'PHEV',
        'hybrid': 'HEV', 'petrol': 'Petrol', 'gasoline': 'Petrol', 'diesel': 'Diesel',
        'lpg':'Other','cng':'Other','other':'Other'
    }
    df['category'] = df['fuel_norm'].map(mapping).fillna('Other')
    piv = df.groupby(['year','category'])['value'].sum().unstack(fill_value=0).reset_index()
    piv['region'] = region_name
    return piv

# Example usage (will skip loading if files missing)
frames = []
for region, path in files_expected.items():
    if os.path.exists(path):
        p = load_and_pivot(path, region if region!='Global_EV' else 'Global')
        if p is not None:
            frames.append(p)

if frames:
    df_h = pd.concat(frames, ignore_index=True).fillna(0)
    # Add missing standard columns
    for c in ['BEV','PHEV','HEV','Petrol','Diesel','Other']:
        if c not in df_h.columns:
            df_h[c] = 0
    # Compute totals
    df_h['total'] = df_h[['BEV','PHEV','HEV','Petrol','Diesel','Other']].sum(axis=1)
    save_csv(df_h, 'harmonized_registrations.csv')
else:
    print("No source files loaded. Please populate ./data/ with the source CSVs as described in the notebook.")

# --- 7) Plotting for available regions
props = ['BEV','PHEV','HEV','Petrol','Diesel','Other']
regions_available = df_h['region'].unique().tolist() if 'df_h' in globals() else []
for r in regions_available:
    stacked_chart(df_h, r, props, kind='absolute')
    stacked_chart(df_h, r, props, kind='share')

# --- 8) EU and Global yearly summary tables (split percentages)
if 'df_h' in globals():
    summary = df_h.groupby(['region','year'])[props].sum().reset_index()
    # Compute shares
    for p in props:
        summary[p + '_share'] = summary[p] / summary[props].sum(axis=1)
    save_csv(summary, 'yearly_summary_with_shares.csv')
    print("Charts and CSVs saved in", outdir)
else:
    print("Harmonized dataframe not available; load source files and re-run.")
