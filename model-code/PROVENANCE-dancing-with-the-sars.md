# Provenance: dancing-with-the-sars
Staged 2026-11-12 (ET). No login used.
- sen1floods11/ : Sen1Floods11 v1.1 hand-labelled subset (S1Hand VV/VH dB, LabelHand, S1OtsuLabelHand, JRCWaterHand, splits, metadata geojson).
  Source: gs://sen1floods11 via https://storage.googleapis.com/sen1floods11/v1.1/ . Bonafilia et al., CVPRW 2020. Licence: CC-BY-4.0.
- s1_rtc_valencia/*.tif : Sentinel-1 RTC (gamma0, linear power, VV/VH, 10 m) clips, bbox -0.50,39.30,-0.30,39.46, 2024-09-15..2024-12-15
  (Valencia DANA flood 29 Oct 2024). Source: Microsoft Planetary Computer collection sentinel-1-rtc (anonymous SAS token).
  Licence: Copernicus Sentinel data (free, full and open); RTC processing by Catalyst/Microsoft under CC-BY-4.0. provenance.json lists item ids.
  Note: file suffix "_rtc" is a naming quirk; asc/des is in the name.
- nisar_granules_cmr.json : NASA CMR metadata for NISAR L2 GCOV (V1, BETA, PROVISIONAL) and GUNW granules over Valencia, Toronto, Jasper.
- nisar_browse/{aoi}/*.png : public NISAR GCOV browse PNGs from https://nisar.asf.earthdatacloud.nasa.gov/BROWSE/ (no login).
Needs Earthdata login (NOT downloaded): NISAR .h5 products (GCOV/GUNW/GSLC, ~4.6 GB each) from ASF DAAC, OPERA RTC-S1/DSWx-S1/DIST-S1, ASF HyP3.
NISAR data are NASA/ISRO open data, no restrictions; cite ASF DAAC.
