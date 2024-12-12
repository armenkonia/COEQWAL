# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 08:40:43 2024

@author: armen
"""

import pyhecdss
import pandas as pd
import numpy as np

fname=r"C:\Users\armen\Desktop\COEQWAL\Datasets\calsim\calsim scenarios\s0002_DCR2023_9.3.1_danube_adj-20241012T184038Z-001\s0002_DCR2023_9.3.1_danube_adj\Model_Files\9.3.1_danube_adj\DSS\output\DCR2023_DV_9.3.1_v2a_Danube_Adj_v1.8.dss"
#75
fname=r"C:\Users\armen\Downloads\s0004_DCR2023_9.3.1_danube_cc75-20241204T034615Z-001\s0004_DCR2023_9.3.1_danube_cc75\Model_Files\9.3.1_danube_cc75\DSS\output\DCR2023_DV_9.3.1_Danube_CC75_v1.8.dss"
#95
# fname=r"C:\Users\armen\Downloads\s0005_DCR2023_9.3.1_danube_cc95-20241204T034613Z-001\s0005_DCR2023_9.3.1_danube_cc95\Model_Files\9.3.1_danube_cc95\DSS\output\DCR2023_DV_9.3.1_Danube_CC95_v1.8.dss"
#50
# fname=r"C:\Users\armen\Downloads\s0003_DCR2023_9.3.1_danube_cc50-20241204T034618Z-001\s0003_DCR2023_9.3.1_danube_cc50\Model_Files\9.3.1_danube_cc50\DSS\output\DCR2023_DV_9.3.1_Danube_cc50_v1.8.dss"


with pyhecdss.DSSFile(fname) as d:
    meta_dss=d.read_catalog()

def build_dss_path(row):
    return f"/{row['A']}/{row['B']}/{row['C']}/{row['D']}/{row['E']}/{row['F']}/"

du_meta_df = pd.read_excel(r"C:\Users\armen\Desktop\COEQWAL\Datasets\calsim\cs3rpt2022_all_demand_units_v20241003.xlsx", sheet_name='all_demand_units_updated', header=1)
du_ag = du_meta_df[du_meta_df['Unit Type (Ag, MI, Refuge/Wetland)'] == 'AG']
du_ag = du_ag.dropna(subset=['Delivery_Variable'])
duplicate_du = du_ag[du_ag['Demand Unit'].duplicated(keep=False)] #lists all duplicated du
du_ag = du_ag.drop_duplicates(subset=['Demand Unit'])
du_ag_only = du_ag[['Demand Unit']].iloc[:, 0]

#%%
du_ag_dv = {}
for demand_unit in du_ag_only.unique():
    # df = meta_dss[meta_dss['B'].str.contains(demand_unit, na=False)]
    df = meta_dss[meta_dss['B'].str.endswith(demand_unit, na=False)]
    du_ag_dv[demand_unit] = df
#%%

# du_ag_dn = {}
# lengths = []
# for key, df in du_ag_dv.items():
#     # filtered_df = df[df['B'].str.startswith('DN_', na=False) & df['B'].str.endswith(key, na=False)]
#     filtered_df = df[df['B'] == 'DN_' + key]
#     du_ag_dn[key] = filtered_df
#     lengths.append({'key': key, 'length': len(filtered_df)})
# dn_df = pd.DataFrame(lengths)

def filter_and_track_lengths(du_ag_dv, prefix):
    filtered_dict = {}
    lengths = []
    
    # Filter each DataFrame based on the prefix and store lengths
    for key, df in du_ag_dv.items():
        filtered_df = df[df['B'] == f'{prefix}{key}']
        filtered_dict[key] = filtered_df
        lengths.append({'key': key, 'length': len(filtered_df)})
    
    # Convert lengths to a DataFrame
    lengths_df = pd.DataFrame(lengths)
    
    return filtered_dict, lengths_df

du_ag_dn, dn_df = filter_and_track_lengths(du_ag_dv, 'DN_')
du_ag_ru, ru_df = filter_and_track_lengths(du_ag_dv, 'RU_')
du_ag_aw, aw_df = filter_and_track_lengths(du_ag_dv, 'AW_')
du_ag_gp, gp_df = filter_and_track_lengths(du_ag_dv, 'GP_')
du_ag_gp, gp_df = filter_and_track_lengths(du_ag_dv, 'GP_')
du_ag_rp, rp_df = filter_and_track_lengths(du_ag_dv, 'RP_')

meta_df = pd.merge(dn_df, gp_df, on='key')
meta_df = pd.merge(meta_df, ru_df, on='key')
meta_df = pd.merge(meta_df, aw_df, on='key', suffixes=('_left', '_right'))
meta_df.columns = ['Demand Unit', 'Surface Water - net', 'Groundwater Pumping','Reuse', 'Applied Water']

#%%
# du_ag_aw_ts = {}
# for key, df in du_ag_dv.items():
#     filtered_df = df[df['B'] == 'AW_' + key]
#     if not filtered_df.empty:
#         filtered_df = filtered_df.iloc[0]
#         pathname = build_dss_path(filtered_df)         
#         df, units2, ptype2 = d.read_rts(pathname)
#         du_ag_aw_ts[key] = df
#     else:
#         continue
# combined_df = pd.concat(du_ag_aw_ts.values(), axis=1) 
# combined_df.columns = du_ag_aw_ts.keys()
# empty_keys = [key for key, df in du_ag_aw.items() if df.empty]
# for key in empty_keys:
#     combined_df[key] = np.nan

def process_data(prefix, data_dict, meta_dict):
    result_dict = {}

    for key, df in data_dict.items():
        # Filter based on the given prefix
        filtered_df = df[df['B'] == prefix + key]
        if not filtered_df.empty:
            filtered_row = filtered_df.iloc[0]
            pathname = build_dss_path(filtered_row)
            df, units2, ptype2 = d.read_rts(pathname)
            result_dict[key] = df
        else:
            continue

    # Concatenate the result dictionary into a DataFrame
    combined_df = pd.concat(result_dict.values(), axis=1)
    combined_df.columns = result_dict.keys()

    # # Find keys with empty DataFrames and add them as empty columns
    # empty_keys = [key for key, df in meta_dict.items() if df.empty]
    # empty_columns_df = pd.DataFrame({key: np.nan for key in empty_keys}, index=combined_dn_df.index)
    # combined_df = pd.concat([combined_df, empty_columns_df], axis=1)
    # combined_df = combined_df.sort_index(axis=1)
    return combined_df

combined_aw_df = process_data('AW_', du_ag_dv, du_ag_aw)
combined_dn_df = process_data('DN_', du_ag_dv, du_ag_dn)
combined_gp_df = process_data('GP_', du_ag_dv, du_ag_gp)
combined_ru_df = process_data('RU_', du_ag_dv, du_ag_ru)
combined_rp_df = process_data('RP_', du_ag_dv, du_ag_rp)

combined_sum_df_1 = combined_gp_df.fillna(0) + combined_ru_df.fillna(0) + combined_dn_df.fillna(0) 
combined_sum_df_2 = combined_aw_df.fillna(0) + combined_rp_df.fillna(0)

#%%
aw_df = pd.melt(
    combined_aw_df.reset_index(),     # Reset index to make the time series part of the data
    id_vars=['index'],                # Specify 'index' (time series) as an identifier variable
    var_name='Demand Unit',           # New column name for demand units
    value_name='Applied Water')         # New column name for demand values

dn_df = pd.melt(
    combined_dn_df.reset_index(), 
    id_vars=['index'],
    var_name='Demand Unit',
    value_name='Net Diversion')

gp_df = pd.melt(
    combined_gp_df.reset_index(),
    id_vars=['index'],
    var_name='Demand Unit',
    value_name='Groundwater Pumping')

ru_df = pd.melt(
    combined_ru_df.reset_index(),     
    id_vars=['index'], 
    var_name='Demand Unit',
    value_name='Reuse')

rp_df = pd.melt(
    combined_rp_df.reset_index(),     
    id_vars=['index'], 
    var_name='Demand Unit',
    value_name='Riparian')
#%%
merged_df = pd.merge(aw_df,dn_df, how='outer', on=['index','Demand Unit'])
merged_df = pd.merge(merged_df,gp_df, how='outer', on=['index','Demand Unit'])
merged_df = pd.merge(merged_df,ru_df, how='outer', on=['index','Demand Unit'])
merged_df = pd.merge(merged_df,rp_df, how='outer', on=['index','Demand Unit'])
merged_df = merged_df.sort_values(by=['Demand Unit', 'index'])
merged_df.set_index('index',inplace=True)
merged_df.to_csv('calsim_deliveries_cc75.csv')
