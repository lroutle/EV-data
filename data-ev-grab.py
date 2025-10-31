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
data_dir = 'data'
os.makedirs(data_dir, exist_ok=True)

# --- Helper functions
def save_csv(df, name):
    path = os.path.join(data_dir, name)
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
def download_eurostat_data():
    """
    Downloads and processes Eurostat vehicle registration data.
    """
    try:
        from eurostat import get_data_df
        df = get_data_df('road_eqr_carpda')

        # Reshape the data
        id_vars = ['freq', 'unit', 'mot_nrg', 'geo\\TIME_PERIOD']
        value_vars = [col for col in df.columns if col not in id_vars]
        df = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name='year', value_name='value')

        # Rename columns and filter
        df = df.rename(columns={'mot_nrg': 'fuel', 'geo\\TIME_PERIOD': 'country'})
        df['year'] = df['year'].astype(int)

        # Map fuel types
        fuel_mapping = {
            'TOTAL': 'Total',
            'BEV': 'BEV',
            'PHEV': 'PHEV',
            'HEV': 'HEV',
            'ALT': 'Other',
            'OTH': 'Other',
            'PET': 'Petrol',
            'DIESEL': 'Diesel',
            'ELEC': 'BEV'
        }
        df['fuel'] = df['fuel'].map(fuel_mapping).fillna('Other')

        # Aggregate by year and fuel type
        df = df.groupby(['year', 'fuel'])['value'].sum().reset_index()

        # Pivot the table
        df_pivot = df.pivot(index='year', columns='fuel', values='value').fillna(0).reset_index()

        # Save to CSV
        save_csv(df_pivot, 'eurostat_reg.csv')

    except Exception as e:
        print(f"Could not download or process Eurostat data: {e}")

download_eurostat_data()

# --- 2) Global BEV/PHEV consolidated series (OWID / EVVolumes)
def download_owid_data():
    """
    Downloads and processes OWID EV sales data.
    """
    try:
        owid_ev_url = "https://ourworldindata.org/grapher/ev-sales.csv"
        r = requests.get(owid_ev_url)
        if r.ok:
            ev_owid = pd.read_csv(io.StringIO(r.text))
            save_csv(ev_owid, 'global_ev.csv')
        else:
            print("Could not fetch OWID EV sales CSV; please download manually and place in data/")

    except Exception as e:
        print(f"Could not download or process OWID data: {e}")

download_owid_data()

# --- 3) Read local/manual files into harmonized dataframe
files_expected = {
    'EU': os.path.join(data_dir, 'eurostat_reg.csv'),
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

    if 'fuel' not in df.columns:
        # Reshape the data
        id_vars = [col for col in df.columns if col.lower() in ['year', 'region', 'country', 'code', 'entity']]
        value_vars = [col for col in df.columns if col.lower() not in ['year', 'region', 'country', 'code', 'entity']]
        df = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name='fuel', value_name='value')

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

# --- 4) Plotting for available regions
props = ['BEV','PHEV','HEV','Petrol','Diesel','Other']
regions_available = df_h['region'].unique().tolist() if 'df_h' in globals() else []
for r in regions_available:
    stacked_chart(df_h, r, props, kind='absolute')
    stacked_chart(df_h, r, props, kind='share')

# --- 5) EU and Global yearly summary tables (split percentages)
if 'df_h' in globals():
    summary = df_h.groupby(['region','year'])[props].sum().reset_index()
    # Compute shares
    for p in props:
        summary[p + '_share'] = summary[p] / summary[props].sum(axis=1)
    save_csv(summary, 'yearly_summary_with_shares.csv')
    print("Charts and CSVs saved in", outdir)
else:
    print("Harmonized dataframe not available; load source files and re-run.")
