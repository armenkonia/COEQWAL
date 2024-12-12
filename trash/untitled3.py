# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 09:32:02 2024

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
sac_id = sac_id.to_crs(hr.crs)
sj_id = sj_id.to_crs(hr.crs)
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

#%%
landiq_20.columns
landiq_20_selected = landiq_20.loc[landiq_20.HYDRO_RGN == 'San Joaquin River']
landiq_20_selected.plot()

landiq_20_selected_overlay = landiq_20_selected.overlay(cv_id, how='identity')
