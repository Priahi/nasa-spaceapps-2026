# Handoff from the site worker (10:12 AM ET)
Already done here before the split (Earthdata login via ~/.netrc, written from EARTHDATA_PASSWORD by trends/setup_netrc.py, never printed):
- OPERA DSWx-S1 (PO.DAAC) Valencia, 44 granules x (B01_WTR, B03_CONF) in opera/; processed by opera_valencia.py -> out/opera_valencia.json + out/opera_{before,after}_*.png.
  Result: new water outside usual water 30.7 km2 (26 Oct asc) -> 77.7 km2 (31 Oct asc), 18 passes 1 Oct-19 Nov 2024. Site already wires this in.
- GRACE/GRACE-FO JPL RL06.3 mascon CRI v04: trends/raw/grace/grace.nc (sha256 3522dd57...), trends/analyze_earthdata.py (land cells, deseasonalised annual means 2003-2025, 2017+2018 dropped <6 months).
  Valencia decreasing p=0.0019 (-0.39 cm/yr); Ontario increasing p=0.014 (pHR 0.039, +0.55 cm/yr); Iowa no trend p=0.57. Stored in trends/out/trends.json["earthdata"]["grace"].
- STILL DOWNLOADING in background (dl.sh via xargs, urls.txt, granules.json): MCD64A1 h11v03 Apr-Oct 2003-2025 (161 files) into mcd64/, HLS L30/S30 T15TVG Jul-Aug 2024/2025 (<=5% cloud; red, NIR, Fmask) into hls/. Not processed. The Earthdata worker can take these over (kill with: pkill -f dl.sh).
- GES DISC (GPM IMERG, GLDAS) BLOCKED: 'Pre authorization required' -> Parsa must approve app at https://urs.earthdata.nasa.gov/approve_app?client_id=e2WVk8Pw6weeLUKZYOxvTQ. On-prem OPeNDAP (gpm1/hydro1) returns 410 retired; trends/fetch_gesdisc.py is pointed at Earthdata Cloud OPeNDAP (untested until approval).
