# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 00:31:05 2024

@author: armen
"""
import pandas as pd
del_vars = pd.read_csv('delivery_variables.csv')
du_del_var = pd.read_csv('demand_unit_with_delivery_variables.csv')

# df_grouped = du_del_var.groupby('Demand Unit')['Delivery_Variable_new'].apply(lambda x: ', '.join(set(x))).reset_index()
#%%
# filtered_df = du_del_var[du_del_var['Demand Unit'] == '06_NA']

# df_dict = {}
# # Loop through unique 'Delivery_Variable_new' values for '06_NA'
# for i in filtered_df['Delivery_Variable_new']:
#     df = del_vars.loc[del_vars['Delivery Variable'] == i]
#     df_dict[i] = df

# # Now df_dict will have 'Delivery_Variable_new' as keys and corresponding DataFrames as values


#%%
# this stores delivery variables for each demand unit
du_dict = {} # to store delivery unit
for du in du_del_var['Demand Unit'].unique():
    dv_dict = {}
    du_df = du_del_var[du_del_var['Demand Unit'] == du]
    for i in du_df['Delivery_Variable_new']:
        dv_dict[i] = del_vars.loc[del_vars['Delivery Variable'] == i]
    du_dict[du] = dv_dict

#this get total deliveries for each demand unit
merged_df_dict = {}
for du, df_dict in du_dict.items():
    if len(df_dict) > 1:  # Check if there is more than one Delivery variable for the current Demand Unit
        merged_df = next(iter(df_dict.values()))
        for df in list(df_dict.values())[1:]:
            merged_df = merged_df.merge(df, on='index', how='outer')
            merged_df['Deliveries'] = merged_df['Deliveries_x'] + merged_df['Deliveries_y']
            
            # Drop 'Unnamed' columns
            # merged_df = merged_df.drop(columns=df.filter(like='Unnamed: 0_x').columns)
            
            # Rename 'Deliveries_x' and 'Deliveries_y' based on the first values in the respective columns
            merged_df = merged_df.rename(columns={
                'Deliveries_x': f"{merged_df['Delivery Variable_x'].iloc[0]}_Deliveries",
                'Deliveries_y': f"{merged_df['Delivery Variable_y'].iloc[0]}_Deliveries"
            })
            # merged_df = merged_df.drop(columns=['Delivery Variable_x', 'Delivery Variable_y'])

            merged_df = merged_df.drop(columns=['Unnamed: 0_x', 'Unnamed: 0_y', 'Delivery Variable_x', 'Delivery Variable_y'])
        merged_df_dict[du] = merged_df
    elif len(df_dict) == 1:
        merged_df = next(iter(df_dict.values()))
        if merged_df.empty:
            merged_df_dict[du] = merged_df  # Assign the empty DataFrame
        else:
            delivery_variable_name = merged_df['Delivery Variable'].iloc[0] 
            merged_df = merged_df.rename(columns={
                'Deliveries': f"{delivery_variable_name}_Deliveries"})
            # Drop unnecessary columns if they exist
            merged_df = merged_df.drop(columns=['Unnamed: 0', 'Delivery Variable'])
            merged_df_dict[du] = merged_df
