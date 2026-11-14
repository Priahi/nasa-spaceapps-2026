"""List the Earthdata granule files to download for the module upgrades (subsets: only the layers we use)."""
import earthaccess, json
earthaccess.login(strategy="netrc")
out = {}
# SAR Change: OPERA DSWx-S1 surface water over Valencia, before and after the 29 Oct 2024 DANA flood
r = earthaccess.search_data(short_name="OPERA_L3_DSWX-S1_V1", bounding_box=(-0.6, 39.2, -0.2, 39.6), temporal=("2024-10-01", "2024-11-20"), count=100)
out["opera"] = [{"id": g["umm"]["GranuleUR"], "urls": [l for l in g.data_links() if l.endswith(("_B01_WTR.tif", "_B03_CONF.tif"))]} for g in r]
# Hot Spots: MCD64A1 burned area, tile h11v03 (northern Alberta / Saskatchewan boreal), Apr-Oct, 2003-2025
mc = []
for y in range(2003, 2026):
    r = earthaccess.search_data(short_name="MCD64A1", version="061", bounding_box=(-112.6, 57.0, -112.4, 57.2), temporal=(f"{y}-04-01", f"{y}-10-31"), count=50)
    mc += [{"id": g["umm"]["GranuleUR"], "urls": [l for l in g.data_links() if l.endswith(".hdf")]} for g in r if ".h11v03." in g["umm"]["GranuleUR"]]
out["mcd64"] = mc
# Field Shift: HLS L30/S30 over Story County, Jul 2024 and Jul 2025, low cloud
hl = []
for sn in ("HLSL30", "HLSS30"):
    for y in (2024, 2025):
        r = earthaccess.search_data(short_name=sn, version="2.0", bounding_box=(-93.7, 41.86, -93.23, 42.21), temporal=(f"{y}-07-01", f"{y}-08-15"), count=100)
        for g in r:
            cc = next((a["Values"][0] for a in g["umm"].get("AdditionalAttributes", []) if a["Name"] == "CLOUD_COVERAGE"), "100")
            if float(cc) <= 5 and ".T15TVG." in g["umm"]["GranuleUR"]:
                red, nir = ("B04", "B05") if sn == "HLSL30" else ("B04", "B8A")
                hl.append({"id": g["umm"]["GranuleUR"], "cloud": float(cc), "urls": [l for l in g.data_links() if l.endswith((f".{red}.tif", f".{nir}.tif", ".Fmask.tif"))]})
out["hls"] = hl
json.dump(out, open("granules.json", "w"), indent=1)
print({k: len(v) for k, v in out.items()}); print([h["id"] for h in hl])
