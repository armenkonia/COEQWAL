# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 13:36:22 2024

@author: armen
"""


import fiona
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

gdb_path = r"C:\Users\armen\Documents\ArcGIS\Projects\MyProject\MyProject.gdb"
layers = fiona.listlayers(gdb_path)
print(layers)

layer_name = 'landiq_20_no_UX_central_valley_irrigation_districts_center'
landiq_id = gpd.read_file(gdb_path, layer=layer_name)
landiq_id_head = landiq_id.head()
landiq_id = landiq_id[~landiq_id['MAIN_CROP'].isin(['X', 'U'])]
landiq_id = landiq_id[~landiq_id['CLASS2'].isin(['X', 'U'])]

crops = landiq_id['MAIN_CROP'].unique()

sum_acres = landiq_id.groupby('Agency_Nam')[['ACRES']].sum().reset_index()

landiq_id['area_acres'] = landiq_id.geometry.area/ 4046.8564224

#%%
sac_id = gpd.read_file(r"C:\Users\armen\Desktop\COEQWAL\Datasets\ppic-sacramento-valley-delta-surface-water-availability\PPIC_SacramentoValley_SW_Availability_Shapes\ppic-sacramentovalley-sw-availability.shp")
sj_id = gpd.read_file(r"C:\Users\armen\Desktop\COEQWAL\Datasets\ppic-san-joaquin-valley-surface-water-availability\ppic_sjv_sw_availability.shp")
sj_id = sj_id.drop(columns=['OBJECTID_1'])
sac_id = sac_id.rename(columns={'AGENCYNAME': 'Agency_Nam',})
sac_id = sac_id.loc[:, ['Agency_Nam', 'geometry','gross_serv']]
sj_id = sj_id.loc[:, ['Agency_Nam', 'geometry','Service_Ar']]
sac_id = sac_id.rename(columns={'gross_serv': 'Total area',})
sj_id = sj_id.rename(columns={'Service_Ar': 'Total area',})

cv_id = pd.concat([sj_id, sac_id])
cv_id = cv_id.to_crs(epsg=3310)
# cv_id['area_acres'] = cv_id.geometry.area/ 4046.8564224
cv_id['geometry'] = cv_id['geometry'].buffer(0)

cv_id_merged = cv_id.dissolve(by='Agency_Nam', aggfunc='sum')
cv_id = cv_id.drop(columns=['geometry'])

#%%
# merged_df = pd.merge(sum_acres, ag_econ_shp[['Subregion', 'Area_Acre']], on='Subregion', how='left')
merged_df = pd.merge(cv_id_merged,sum_acres, on='Agency_Nam', how='left')
merged_df.rename(columns={'ACRES': 'Irrigated area', 'Area_Acre': 'Total area'}, inplace=True)
#%%
# Calculate the percentage of area irrigated
merged_df['irrigation_ratio'] = merged_df['Irrigated area'] / merged_df['Total area']
merged_df.to_csv('irrigation_district_areas.csv')
# Plot the GeoDataFrame based on the irrigation ratio
fig, ax = plt.subplots(figsize=(12, 12))
merged_df.plot(column='irrigation_ratio', cmap='YlGnBu', legend=True, ax=ax)
# ag_econ_shp.plot(cmap='YlGnBu', legend=True, ax=ax)

# # Customizing the plot
# plt.title('Irrigation Ratio per Area')
# plt.xlabel('Longitude')
# plt.ylabel('Latitude')
# plt.show()

merged_df_areas = merged_df[['Subregion', 'Total area', 'Irrigated area', 'irrigation_ratio']]

