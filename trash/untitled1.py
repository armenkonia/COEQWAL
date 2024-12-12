# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 09:30:35 2024

@author: armen
"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import fiona

landiq_20 = gpd.read_file(r"C:\Users\armen\Desktop\COEQWAL\Datasets\i15_crop_mapping_2020\i15_Crop_Mapping_2020.shp")
sac_id = gpd.read_file(r"C:\Users\armen\Desktop\COEQWAL\Datasets\ppic-sacramento-valley-delta-surface-water-availability\PPIC_SacramentoValley_SW_Availability_Shapes\ppic-sacramentovalley-sw-availability.shp")
sj_id = gpd.read_file(r"C:\Users\armen\Desktop\COEQWAL\Datasets\ppic-san-joaquin-valley-surface-water-availability\ppic_sjv_sw_availability.shp")
hr = gpd.read_file(r"C:\Users\armen\Desktop\COEQWAL\Datasets\i03_Hydrologic_Regions\i03_Hydrologic_Regions.shp")
gwsa = gpd.read_file(r"C:\Users\armen\Desktop\COEQWAL\Datasets\i03_Groundwater_Sustainability_Agencies_MapService\i03_Groundwater_Sustainability_Agencies_MapService.shp")
ag_econ_shp = gpd.read_file(r"C:\Users\armen\Desktop\COEQWAL\Datasets\PPIC_CV_ag regions\PPIC_AgRegions_FIN.shp")
ag_econ_csv = pd.read_csv(r"C:\Users\armen\Desktop\COEQWAL\Datasets\PPIC_database_221211_CV.csv")

gdb_path = r"C:\Users\armen\Desktop\COEQWAL\Datasets\CalSim3_GeoSchematic_20221227.gdb"
# layers = fiona.listlayers(gdb_path)
demand_units = gpd.read_file(gdb_path, layer='i12_CalSim3Model_DemandUnit_20221021')
demand_units = demand_units.to_crs(hr.crs)


landiq_20 = landiq_20.to_crs(hr.crs)
sac_id = sac_id.to_crs(epsg=3310)
sj_id = sj_id.to_crs(epsg=3310)
gwsa = gwsa.to_crs(hr.crs)
ag_econ_shp = ag_econ_shp.to_crs(hr.crs)

# crops = ag_regions_csv.crop.unique()
gwsa.plot()
#%%
sj_id = sj_id.drop(columns=['OBJECTID_1'])
sac_id = sac_id.rename(columns={'AGENCYNAME': 'Agency_Nam',})
sac_id = sac_id.loc[:, ['Agency_Nam', 'geometry']]
sj_id = sj_id.loc[:, ['Agency_Nam', 'geometry']]
cv_id = pd.concat([sj_id, sac_id])

gdb_path = r"C:\Users\armen\Documents\ArcGIS\Projects\MyProject\MyProject.gdb"
cv_id.to_file(gdb_path, layer='central_valley_irrigation_districts', driver="GPKG")

# fig, ax = plt.subplots(figsize=(12, 12))
# hr.plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.8)
# cv_id.plot(ax=ax, color='red', edgecolor='green', alpha=0.1)
# plt.show()

#%%
#merge landiq with irrigation districts
landiq_20_cv_id = gpd.sjoin(landiq_20, cv_id, how='left', predicate='intersects')
landiq_20_cv_id = landiq_20_cv_id.rename(columns={'index_right': 'index_cv_id'})
landiq_20_cv_id['Agency_Nam'] = landiq_20_cv_id['Agency_Nam'].fillna('no irrigation district')

# fig, ax = plt.subplots(figsize=(12, 12))
# hr.plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.5)
# cv_id.plot(ax=ax, facecolor='none', edgecolor='orange', alpha=0.5)
# # landiq_20_cv_id.plot(ax=ax, color='green', edgecolor=None, alpha=0.8)
# landiq_20_cv_id.plot(ax=ax, column='Agency_Nam', legend=False, edgecolor=None, alpha=0.8)
# plt.show()

#%%
#merge landiq+id with gwsa
landiq_20_cv_id_gwsa = gpd.sjoin(landiq_20_cv_id, gwsa, how='left', predicate='intersects')
landiq_20_cv_id_gwsa = landiq_20_cv_id_gwsa.rename(columns={'index_right': 'index_gwsa'})

# fig, ax = plt.subplots(figsize=(12, 12))
# hr.plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.5)
# gwsa.plot(ax=ax, facecolor='none', edgecolor='orange', alpha=0.5)
# landiq_20_cv_id_gwsa.plot(ax=ax, color='green', edgecolor=None, alpha=0.8)
# plt.show()

#%%
#merge landiq+id+gwsa with du
landiq_20_cv_id_gwsa_du = gpd.sjoin(landiq_20_cv_id_gwsa, demand_units, how='left', predicate='intersects')
landiq_20_cv_id_gwsa_du = landiq_20_cv_id_gwsa_du.rename(columns={'index_right': 'index_du'})

# fig, ax = plt.subplots(figsize=(12, 12))
# hr.plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.5)
# demand_units.plot(ax=ax, facecolor='none', edgecolor='orange', alpha=0.5)
# landiq_20_cv_id_gwsa_du.plot(ax=ax, color='green', edgecolor=None, alpha=0.8)
# plt.show()

#%%
#merge landiq+id+gwsa+du with ag_econ
landiq_20_cv_id_gwsa_du_econ = gpd.sjoin(landiq_20_cv_id_gwsa_du, ag_econ_shp, how='left', predicate='intersects')
landiq_20_cv_id_gwsa_du_econ = landiq_20_cv_id_gwsa_du_econ.rename(columns={'index_right': 'index_econ'})
  

landiq_20_ag_regions_1 = gpd.overlay(landiq_20, ag_regions, how='identity')


