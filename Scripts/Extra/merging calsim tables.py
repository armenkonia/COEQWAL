# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 08:27:33 2024

@author: armen
"""

import pandas as pd
import matplotlib.pyplot as plt

excel_path = r"C:\Users\armen\Desktop\COEQWAL\Calsim Report Tables.xlsx"
excel_file = pd.ExcelFile(excel_path)
sheet_names = excel_file.sheet_names
du_sac = pd.read_excel(excel_path,sheet_name=sheet_names[0])
du_sj_tl = pd.read_excel(excel_path,sheet_name=sheet_names[3])
div_sac = pd.read_excel(excel_path,sheet_name=sheet_names[1])
div_fthr = pd.read_excel(excel_path,sheet_name=sheet_names[2])

div_sac['Area (acres)'] = div_sac['Area (acres)'].ffill()
du_sac.iloc[:, 0] = du_sac.iloc[:, 0].ffill()
du_sj_tl.iloc[:, 0] = du_sj_tl.iloc[:, 0].ffill()
div_sac.iloc[:, 0] = div_sac.iloc[:, 0].ffill()
div_fthr.iloc[:, 0] = div_fthr.iloc[:, 0].ffill()

du_sac_sj_tl = pd.concat([du_sac,du_sj_tl], axis=0)
div_sac_fthr = pd.concat([div_sac,div_fthr], axis=0)

#%%
CVP_sac_stlmnnt_cntrs = pd.read_excel(r"C:\Users\armen\Desktop\COEQWAL\Datasets\Calsim report tables.xlsx",sheet_name='Table 11-18')
CVP_sac_srvc_cntrs = pd.read_excel(r"C:\Users\armen\Desktop\COEQWAL\Datasets\Calsim report tables.xlsx",sheet_name='Table 11-19')
orlando_solano_projects = pd.read_excel(r"C:\Users\armen\Desktop\COEQWAL\Datasets\Calsim report tables.xlsx",sheet_name='Table 11-20')
SJ_eastside_diversion = pd.read_excel(r"C:\Users\armen\Desktop\COEQWAL\Datasets\Calsim report tables.xlsx",sheet_name='Table 11-21')

CVP_sac_stlmnnt_cntrs = CVP_sac_stlmnnt_cntrs.iloc[1:-1]
CVP_sac_srvc_cntrs = CVP_sac_srvc_cntrs.iloc[1:-1]
orlando_solano_projects = orlando_solano_projects.iloc[1:-1]
SJ_eastside_diversion = SJ_eastside_diversion.iloc[1:-1]

orlando_solano_projects = orlando_solano_projects.ffill()
SJ_eastside_diversion = SJ_eastside_diversion.ffill()

orlando_solano_projects['Historical Delivery'] = pd.to_numeric(orlando_solano_projects['Historical Delivery'], errors='coerce')
orlando_solano_projects = orlando_solano_projects.groupby(["Demand Unit", "Water Purveyor"])["Historical Delivery"].sum().reset_index()

SJ_eastside_diversion['Historical Diversion'] = pd.to_numeric(SJ_eastside_diversion['Historical Diversion'], errors='coerce')
SJ_eastside_diversion = SJ_eastside_diversion.groupby(["Demand Unit", "Water Purveyor"])["Historical Diversion"].sum().reset_index()

CVP_contractors = pd.concat([CVP_sac_stlmnnt_cntrs, CVP_sac_srvc_cntrs])
#%%
du_waterunit_sum = pd.read_csv(r"C:\Users\armen\Desktop\COEQWAL\Datasets\DU_wateruse.csv")
CVP_sac_srvc_cntrs = CVP_sac_srvc_cntrs.merge(du_waterunit_sum, left_on=['Demand Unit'], right_on=['DU_ID'], how='left')

df = CVP_sac_srvc_cntrs.copy()
# Set the bar width and positions
bar_width = 0.25
positions = range(len(df))

# Create a bar plot
plt.bar(positions, df['Historical Delivery'], width=bar_width, label='Historical Delivery', color='blue', align='center')
plt.bar([p + bar_width for p in positions], df['total_wateruse_TAF'], width=bar_width, label='total wateruse', color='orange', align='center')

# Adding labels and title
plt.xlabel('Data Points')
plt.ylabel('Values')
plt.title('Contract Amount vs Historical and Simulated Delivery')
plt.xticks([p + bar_width for p in positions], [f'Point {i+1}' for i in range(len(df))])  # Custom x-tick labels
plt.legend()

# Show plot
plt.tight_layout()
plt.show()
