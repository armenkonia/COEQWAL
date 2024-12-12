# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 20:26:00 2024

@author: armen
"""
#checking if the demand units are the same, im not looking at any other column
import pandas as pd

DU_SJ_TL = pd.read_excel(r"C:\Users\armen\Desktop\COEQWAL\Datasets\Calsim report tables.xlsx", sheet_name = 'Table 3-6 SJ TL Ag DU')
DU_SJ_TL['Demand Unit'] = DU_SJ_TL['Demand Unit'].ffill()

DU_Sac = pd.read_excel(r"C:\Users\armen\Desktop\COEQWAL\Datasets\Calsim report tables.xlsx", sheet_name = 'Table 3-3 Sac Ag DU')
DU_Sac['Demand Unit'] = DU_Sac['Demand Unit'].ffill()

DU_ag = pd.concat([DU_SJ_TL, DU_Sac])
DU_ag = DU_ag.sort_values(by='Demand Unit')

#%%
DU_all = pd.read_excel(r"C:\Users\armen\Desktop\COEQWAL\calsim\cs3rpt2022_all_demand_units_v20241003.xlsx",sheet_name='all_demand_units',header=1)
DU_all_ag = DU_all.loc[DU_all['Unit Type (Ag, MI, Refuge/Wetland)'] == 'AG']
DU_all_ag = DU_all_ag.sort_values(by='Demand Unit')

#%%%
DU_all_ag.reset_index(drop=True, inplace=True)
DU_ag.reset_index(drop=True, inplace=True)
DU_all_ag['Demand Unit'].equals(DU_ag['Demand Unit'])
differences = DU_all_ag['Demand Unit'][DU_all_ag['Demand Unit'] != DU_ag['Demand Unit']]
