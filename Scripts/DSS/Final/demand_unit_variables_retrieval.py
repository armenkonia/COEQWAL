# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 15:22:07 2024

@author: armen
"""

import pyhecdss
import pandas as pd
import numpy as np
from zipfile import ZipFile 
import os
# extract dss from nested zip files
main_zip_file = "s0004_DCR2023_9.3.1_danube_cc75-20241204T034615Z-001.zip"
main_extract_path = os.path.splitext(main_zip_file)[0]
os.makedirs(main_extract_path, exist_ok=True)
with ZipFile(main_zip_file, 'r') as zip_ref:
    zip_ref.extractall(main_extract_path)

nested_zip_file = os.path.join(main_extract_path, "s0004_DCR2023_9.3.1_danube_cc75", "Model_Files", "9.3.1_danube_cc75.zip")
nested_extract_path = os.path.splitext(nested_zip_file)[0]
os.makedirs(nested_extract_path, exist_ok=True)
with ZipFile(nested_zip_file, 'r') as zip_ref:
    zip_ref.extractall(nested_extract_path)

dss_file_path = os.path.join(nested_extract_path, "DSS", "output", "DCR2023_DV_9.3.1_Danube_CC75_v1.8.dss")
metadata_file_path = r"C:\Users\armen\Desktop\COEQWAL\Datasets\calsim\cs3rpt2022_all_demand_units_v20241003.xlsx"
#%%
def process_dss_data_for_units(dss_file_path, metadata_file_path, dss_path, output_path):
    # Open the DSS file
    with pyhecdss.DSSFile(dss_file_path) as dss:
        dss_metadata = dss.read_catalog()

    # Define utility function to build DSS path
    def build_dss_path(row):
        return f"/{row['A']}/{row['B']}/{row['C']}/{row['D']}/{row['E']}/{row['F']}/"

    # Obtain Ag DUs
    du_meta = pd.read_excel(metadata_file_path, sheet_name='all_demand_units_updated', header=1)
    ag_du = du_meta[du_meta['Unit Type (Ag, MI, Refuge/Wetland)'] == 'AG']
    ag_du = ag_du.dropna(subset=['Delivery_Variable'])
    unique_ag_du = ag_du[['Demand Unit']].drop_duplicates()

    # Group DSS metadata by demand units
    def group_metadata_by_demand_unit(metadata, demand_units):
        grouped = {}
        for unit in demand_units:
            filtered = metadata[metadata['B'].str.endswith(unit, na=False)]
            grouped[unit] = filtered
        return grouped

    dss_grouped_metadata = group_metadata_by_demand_unit(dss_metadata, unique_ag_du['Demand Unit'])

    # Filter metadata by prefixes and track lengths
    def filter_metadata_by_prefix(metadata_group, prefix):
        filtered_metadata = {}
        lengths = []
        for unit, df in metadata_group.items():
            filtered_df = df[df['B'] == f"{prefix}{unit}"]
            filtered_metadata[unit] = filtered_df
            lengths.append({'Demand Unit': unit, 'Length': len(filtered_df)})
        return filtered_metadata, pd.DataFrame(lengths)

    # Filter metadata by various prefixes
    metadata_dn, lengths_dn = filter_metadata_by_prefix(dss_grouped_metadata, 'DN_')
    metadata_ru, lengths_ru = filter_metadata_by_prefix(dss_grouped_metadata, 'RU_')
    metadata_aw, lengths_aw = filter_metadata_by_prefix(dss_grouped_metadata, 'AW_')
    metadata_gp, lengths_gp = filter_metadata_by_prefix(dss_grouped_metadata, 'GP_')
    metadata_rp, lengths_rp = filter_metadata_by_prefix(dss_grouped_metadata, 'RP_')

    # Combine metadata summaries
    metadata_summary = pd.merge(lengths_dn, lengths_gp, on='Demand Unit')
    metadata_summary = pd.merge(metadata_summary, lengths_ru, on='Demand Unit')
    metadata_summary = pd.merge(metadata_summary, lengths_aw, on='Demand Unit', suffixes=('_left', '_right'))

    # Process data for a specific prefix
    def process_dss_data(prefix, metadata_group, dss_instance):
        processed_data = {}
        for unit, df in metadata_group.items():
            filtered_df = df[df['B'] == f"{prefix}{unit}"]
            if not filtered_df.empty:
                path_row = filtered_df.iloc[0]
                dss_path = build_dss_path(path_row)
                time_series_data, _, _ = dss_instance.read_rts(dss_path)
                processed_data[unit] = time_series_data
        combined_data = pd.concat(processed_data.values(), axis=1)
        combined_data.columns = processed_data.keys()
        return combined_data

    combined_aw = process_dss_data('AW_', metadata_aw, dss)
    combined_dn = process_dss_data('DN_', metadata_dn, dss)
    combined_gp = process_dss_data('GP_', metadata_gp, dss)
    combined_ru = process_dss_data('RU_', metadata_ru, dss)
    combined_rp = process_dss_data('RP_', metadata_rp, dss)

    # Confirm the formulas are correct
    combined_sum_1 = combined_gp.fillna(0) + combined_ru.fillna(0) + combined_dn.fillna(0)
    combined_sum_2 = combined_aw.fillna(0) + combined_rp.fillna(0)

    # Reshape data for merging
    def reshape_for_merging(data, value_name):
        return pd.melt(
            data.reset_index(),
            id_vars=['index'],
            var_name='Demand Unit',
            value_name=value_name)

    aw_reshaped = reshape_for_merging(combined_aw, 'Applied Water')
    dn_reshaped = reshape_for_merging(combined_dn, 'Net Diversion')
    gp_reshaped = reshape_for_merging(combined_gp, 'Groundwater Pumping')
    ru_reshaped = reshape_for_merging(combined_ru, 'Reuse')
    rp_reshaped = reshape_for_merging(combined_rp, 'Riparian')

    merged_data = aw_reshaped
    for df in [dn_reshaped, gp_reshaped, ru_reshaped, rp_reshaped]:
        merged_data = pd.merge(merged_data, df, how='outer', on=['index', 'Demand Unit'])

    merged_data = merged_data.sort_values(by=['Demand Unit', 'index']).set_index('index')

    # Save merged data to the specified output path
    merged_data.to_csv(output_path)

    return merged_data

dss_file_path = dss_file_path
metadata_file_path = metadata_file_path
output_path = 'calsim_deliveries_cc75.csv'

merged_data = process_dss_data_for_units(dss_file_path, metadata_file_path, output_path=output_path)