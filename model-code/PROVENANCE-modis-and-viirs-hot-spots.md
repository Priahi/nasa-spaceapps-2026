# Provenance: modis-and-viirs-hot-spots
Staged 2026-11-12 (ET) by box script. No login, no API key used.
- firms_country/modis_{2000..2025}_{Canada,Argentina}.csv : NASA FIRMS MODIS C6.1 active fire archive (Terra+Aqua), country files.
  URL pattern: https://firms.modaps.eosdis.nasa.gov/data/country/modis/{year}/modis_{year}_{Country}.csv
- firms_country/viirs-snpp_{2012..2025}_{Canada,Argentina}.csv : NASA FIRMS VIIRS S-NPP 375 m (C2) archive, country files.
  URL pattern: https://firms.modaps.eosdis.nasa.gov/data/country/viirs-snpp/{year}/viirs-snpp_{year}_{Country}.csv
- MODIS_C6_1_Global_7d.csv, SUOMI_VIIRS_C2_Global_7d.csv : FIRMS NRT global last-7-days feeds (snapshot 2026-11-12).
Licence: NASA LANCE/FIRMS data are freely available with no restrictions on use; cite
"NASA FIRMS, https://doi.org/10.5067/FIRMS/MODIS/MCD14ML and https://doi.org/10.5067/FIRMS/VIIRS/VNP14IMGT_NRT.002".
Not staged (needs free FIRMS MAP_KEY or Earthdata login): FIRMS area API, VIIRS NOAA-20/NOAA-21 archives, MCD64A1 burned area.
Argentina chosen because the challenge photo credit is CONAE (Argentina); Canada for boreal wildfire.
