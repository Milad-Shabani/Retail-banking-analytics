"""
Final Dashboard Assembly
--------------------------
Combines template.html + dashboard.js + dashboard_data.json + the author
photo into ONE fully self-contained dashboard.html (and a copy at
docs/index.html for GitHub Pages). No external local file dependencies
remain except the Google Fonts / Chart.js CDN references.
"""
import json, os, base64, shutil

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
SRC = os.path.dirname(__file__)
OUT_DASH = os.path.join(BASE, "outputs", "dashboard", "dashboard.html")
OUT_DOCS = os.path.join(BASE, "docs", "index.html")
ASSETS = os.path.join(BASE, "assets")
os.makedirs(os.path.dirname(OUT_DASH), exist_ok=True)
os.makedirs(os.path.dirname(OUT_DOCS), exist_ok=True)

with open(os.path.join(SRC, "template.html")) as f:
    template = f.read()
with open(os.path.join(SRC, "dashboard.js")) as f:
    dashboard_js = f.read()
with open(os.path.join(SRC, "chart.umd.js")) as f:
    chartjs = f.read()
with open(os.path.join(BASE, "outputs", "dashboard", "dashboard_data.json")) as f:
    dashboard_data = f.read()

photo_path = os.path.join(ASSETS, "milad-shabani.jpg")
if os.path.exists(photo_path):
    with open(photo_path, "rb") as f:
        photo_b64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()
else:
    # professional placeholder (initials avatar) if the real photo is not present
    photo_b64 = ("data:image/svg+xml;base64," + base64.b64encode(
        b'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64">'
        b'<rect width="64" height="64" rx="32" fill="#0B1F3A"/>'
        b'<text x="32" y="40" font-size="22" fill="#fff" text-anchor="middle" font-family="Arial">MS</text></svg>'
    ).decode())

dashboard_js_inlined = dashboard_js.replace("__AUTHOR_PHOTO__", photo_b64)

html = template.replace("__DASHBOARD_DATA__", dashboard_data)
html = html.replace("__CHARTJS__", chartjs)
html = html.replace(
    '<script src="dashboard.js"></script>',
    f"<script>\n{dashboard_js_inlined}\n</script>"
)

with open(OUT_DASH, "w") as f:
    f.write(html)
with open(OUT_DOCS, "w") as f:
    f.write(html)

print(f"Dashboard written: {OUT_DASH} ({os.path.getsize(OUT_DASH)/1024:.1f} KB)")
print(f"GitHub Pages copy: {OUT_DOCS}")
