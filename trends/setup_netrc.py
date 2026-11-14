"""Write ~/.netrc for NASA Earthdata from EARTHDATA_USERNAME and EARTHDATA_PASSWORD (never printed)."""
import os, stat
from pathlib import Path
user = os.environ.get("EARTHDATA_USERNAME"); pw = os.environ.get("EARTHDATA_PASSWORD")
if not (user and pw): raise SystemExit("set EARTHDATA_USERNAME and EARTHDATA_PASSWORD")
p = Path.home() / ".netrc"
lines = [l for l in (p.read_text().splitlines() if p.exists() else []) if "urs.earthdata.nasa.gov" not in l]
lines.append(f"machine urs.earthdata.nasa.gov login {user} password {pw}")
p.write_text("\n".join(lines) + "\n"); p.chmod(stat.S_IRUSR | stat.S_IWUSR)
print("netrc written, mode", oct(p.stat().st_mode & 0o777))
