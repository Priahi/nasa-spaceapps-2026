# Provenance: adapting-farms-with-nasa-data  (AOI: Story County, Iowa, FIPS 19169; bbox -93.70,41.86,-93.23,42.21)
Staged 2026-11-12 (ET). No login used.
- cdl_cropscape_story/cdl_{2009..2025}.tif : USDA NASS Cropland Data Layer, county clip via CropScape GetCDLFile (EPSG:5070, 30 m). Public domain (USDA).
  https://nassgeodata.gmu.edu/axis2/services/CDLService/GetCDLFile?year=YYYY&fips=19169 . 2008 by-FIPS file not returned.
- cdl/cdl_{2008..2021}.tif : same CDL from Microsoft Planetary Computer (usda-cdl), bbox clip (different grid from CropScape files).
- dem/nasadem_*.tif : NASADEM elevation, Planetary Computer (nasadem). NASA, public domain.
- modis13q1/*_ndvi.tif : MOD13Q1/MYD13Q1 v061 250 m 16-day NDVI (scaled int16, x0.0001), 2016-2024, Planetary Computer (modis-13Q1-061). NASA LP DAAC, no restrictions.
- power/power_daily_*.json : NASA POWER daily AG community (T2M, T2M_MAX/MIN, PRECTOTCORR, RH2M, ALLSKY_SFC_SW_DWN, GWETROOT, GWETTOP, EVPTRNS, WS2M), 2000-2024, 3x3 points. https://power.larc.nasa.gov/ . NASA, no restrictions.
- soilgrids/*_0-5cm_mean.tif : SoilGrids 2.0 clay, sand, SOC, pH(H2O), bulk density (ISRIC WCS). Licence CC-BY-4.0, cite Poggio et al. 2021.
- nb_cache/ : small cache written by the notebook smoke test.
Needs Earthdata login (NOT downloaded): SMAP L3/L4 soil moisture (NSIDC), ECOSTRESS LST/ET (LP DAAC), GPM IMERG (GES DISC), GRACE/GRACE-FO (PO.DAAC), HLS from LP DAAC (HLS is also on Planetary Computer as hls2-l30/hls2-s30 without login), GEDI.
