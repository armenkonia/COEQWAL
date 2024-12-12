# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 21:29:17 2024

@author: armen
"""

import pyhecdss
import pandas as pd

fname=r"C:\Users\armen\Desktop\COEQWAL\Datasets\s0002_DCR2023_9.3.1_danube_adj-20241012T184038Z-001\s0002_DCR2023_9.3.1_danube_adj\Model_Files\9.3.1_danube_adj\9.3.1_danube_adj\DSS\output\DCR2023_DV_9.3.1_v2a_Danube_Adj_v1.8.dss"
# fname=r"C:\Users\armen\Downloads\0001_draft2023dcr_historical\DSS\output\DCR2023_DV_9.0.0_Danube_Hist_v1.1.dss"
fname=r"C:\Users\armen\Downloads\ForArmen\Exchange\CalSim3_Model_Runs\Scenarios\0001_draft2023dcr_historical\DSS\output\DCR2023_DV_9.0.0_Danube_Hist_v1.1.dss"

with pyhecdss.DSSFile(fname) as d:
    sur_del_meta_df=d.read_catalog()

def build_dss_path(row):
    return f"/{row['A']}/{row['B']}/{row['C']}/{row['D']}/{row['E']}/{row['F']}/"
# first_row = catdf.iloc[0]  
# pathname = build_dss_path(first_row)
# df, units2, ptype2 = d.read_rts(pathname)
# result = catdf[catdf['B'].str.contains('AW_02_NA', na=False)]

du_meta_df = pd.read_excel(r"C:\Users\armen\Desktop\COEQWAL\Datasets\calsim\cs3rpt2022_all_demand_units_v20241003.xlsx", sheet_name='all_demand_units_updated', header=1)
du_ag = du_meta_df[du_meta_df['Unit Type (Ag, MI, Refuge/Wetland)'] == 'AG']
du_ag = du_ag.dropna(subset=['Delivery_Variable'])
du_ag = du_ag.drop_duplicates(subset=['Demand Unit'])
duplicate_du = du_ag[du_ag['Demand Unit'].duplicated(keep=False)]

delivery_vars = du_ag[['Delivery_Variable']].iloc[0:,:]
delivery_vars_duplicates = delivery_vars[delivery_vars.duplicated(keep=False)]
delivery_vars = delivery_vars.drop_duplicates().dropna()

delivery_vars = delivery_vars['Delivery_Variable'].str.split(r'[;|+]', expand=True)
delivery_vars = delivery_vars.stack().str.strip().reset_index(drop=True)

#%%
matches = sur_del_meta_df[sur_del_meta_df['B'].str.contains('71_PA7', na=False)]
matches = sur_del_meta_df[sur_del_meta_df['B'].str.contains('60S_NA2', na=False)] #GW
matches = sur_del_meta_df[sur_del_meta_df['B'].str.contains('60S_NA1', na=False)] #GW

matches = sur_del_meta_df[sur_del_meta_df['B'].str.contains('72_NA2', na=False)] #GW and Su
matches = sur_del_meta_df[sur_del_meta_df['B'].str.contains('50_PA2', na=False)] #GW and Su


#%%
# get metadata of delivery variables for all demand units
delivery_metadf_dic = {}
for del_var in delivery_vars:
    del_var = str(del_var)
    filtered_df = sur_del_meta_df[
        (sur_del_meta_df['B'] == del_var)  # Exact match with del_var
        # (catdf['B'].str.contains(del_var, na=False))
    ]    
    delivery_metadf_dic[del_var] = filtered_df

# get time series of delivery variables for all demand units   
delivery_records_dic  = {}
for key, df_row in delivery_metadf_dic.items():
    if not df_row.empty:  # Check if the row is not empty
        df_row = df_row.iloc[0]
        pathname = build_dss_path(df_row)         
        df, units2, ptype2 = d.read_rts(pathname)
        delivery_records_dic[key]  = df

#convert delivery_records_dic to df
delivery_records_df = pd.concat(delivery_records_dic.values(), axis=1)
delivery_records_df.columns = list(delivery_records_dic.keys())
    
delivery_records_df = delivery_records_df.reset_index()
delivery_records_df = pd.melt(delivery_records_df, id_vars=['index'], 
                  var_name='Delivery Variable', 
                  value_name='Deliveries')
# delivery_records_df.to_csv('delivery_variable_record.csv')

#%%
du_del_vars = du_ag[['Demand Unit','Delivery_Variable']].iloc[0:,:]
du_del_vars[['Delivery_Variable_1', 'Delivery_Variable_2']] = du_del_vars['Delivery_Variable'].str.split(r'[;|+]', expand=True)
du_del_vars['Delivery_Variable_1'] = du_del_vars['Delivery_Variable_1'].str.strip()
du_del_vars['Delivery_Variable_2'] = du_del_vars['Delivery_Variable_2'].str.strip()


stacked_df = du_del_vars.melt(id_vars=['Demand Unit'], value_vars=['Delivery_Variable_1', 'Delivery_Variable_2'],
                      var_name='Delivery_Variable_Number', value_name='Delivery_Variable_new').dropna()
du_del_vars = pd.merge(stacked_df, du_del_vars[['Demand Unit', 'Delivery_Variable']], on='Demand Unit', how='left')
# du_del_vars.to_csv('delivery_variables_of_demand_units.csv')

#%%
# this stores delivery variables for each demand unit
du_dict = {} # to store delivery unit
for du in du_del_vars['Demand Unit'].unique():
    dv_dict = {}
    du_df = du_del_vars[du_del_vars['Demand Unit'] == du]
    for i in du_df['Delivery_Variable_new']:
        dv_dict[i] = delivery_records_df.loc[delivery_records_df['Delivery Variable'] == i]
    du_dict[du] = dv_dict

#this get total deliveries for each demand unit
merged_df_dict = {}
for du, df_dict in du_dict.items():
    if len(df_dict) > 1:  # Check if there is more than one Delivery variable for the current Demand Unit
        merged_df = next(iter(df_dict.values()))
        for df in list(df_dict.values())[1:]:
            merged_df = merged_df.merge(df, on='index', how='outer')
            merged_df['Deliveries'] = merged_df['Deliveries_x'] + merged_df['Deliveries_y']
            # merged_df = merged_df.rename(columns={  # Rename 'Deliveries_x' and 'Deliveries_y' based on the first values in the respective columns
            #     'Deliveries_x': f"{merged_df['Delivery Variable_x'].iloc[0]}_Deliveries",
            #     'Deliveries_y': f"{merged_df['Delivery Variable_y'].iloc[0]}_Deliveries",
            #     'Deliveries': f"{merged_df['Delivery Variable_x'].iloc[0][:2]}_{merged_df['Delivery Variable_y'].iloc[0]}_Deliveries"
            # })
            # merged_df = merged_df.drop(columns=['Delivery Variable_x', 'Delivery Variable_y'])

            merged_df = merged_df.rename(columns={  # Rename 'Deliveries_x' and 'Deliveries_y' based on the first values in the respective columns
                'Deliveries': f"{merged_df['Delivery Variable_x'].iloc[0][:2]}_{merged_df['Delivery Variable_y'].iloc[0]}_Deliveries"
            })
            merged_df = merged_df.drop(columns=['Deliveries_x', 'Deliveries_y'])
            merged_df = merged_df.drop(columns=['Delivery Variable_x', 'Delivery Variable_y'])


        merged_df_dict[du] = merged_df
    elif len(df_dict) == 1:
        merged_df = next(iter(df_dict.values()))
        if merged_df.empty:
            merged_df_dict[du] = merged_df  # Assign the empty DataFrame
        else:
            delivery_variable_name = merged_df['Delivery Variable'].iloc[0] 
            merged_df = merged_df.rename(columns={
                'Deliveries': f"{delivery_variable_name}_Deliveries"})
            merged_df = merged_df.drop(columns=[ 'Delivery Variable'])
            merged_df_dict[du] = merged_df

#%%

for key, df in merged_df_dict.items():
    merged_df_dict[key] = df.set_index('index')

final_df = pd.concat(merged_df_dict.values(), axis=1)
final_df = final_df.dropna(axis=1, how='all')
final_df = final_df.reset_index()
final_df = pd.melt(final_df, id_vars=['index'], var_name='Delivery Variable', value_name='Deliveries')
