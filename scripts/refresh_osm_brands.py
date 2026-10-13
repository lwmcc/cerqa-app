#!/usr/bin/env python3
"""Refreshes scripts/data/osm_fuel_brands.json: branded fuel stations in Mexico from OpenStreetMap
(© OpenStreetMap contributors, ODbL). Run by hand now and then; build_gas_pages.py matches each
CNE station to the nearest branded one within 120 m.  python3 scripts/refresh_osm_brands.py
"""
import json
import os
import urllib.parse
import urllib.request

QUERY = '[out:json][timeout:180];area["ISO3166-1"="MX"]["admin_level"="2"]->.mx;nwr["amenity"="fuel"](area.mx);out center tags;'
# OSM spellings -> one name each
BRANDS = {"pemex": "Pemex", "oxxo": "Oxxo Gas", "oxxo gas": "Oxxo Gas", "petro 7": "Petro Seven", "petro seven": "Petro Seven",
          "total": "TotalEnergies", "totalenergies": "TotalEnergies", "bp": "BP", "g500": "G500", "arco": "ARCO"}


def main():
    data = urllib.parse.urlencode({"data": QUERY}).encode()
    req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=data,
                                 headers={"User-Agent": "cerqa.app gas pages"})
    elements = json.load(urllib.request.urlopen(req, timeout=300))["elements"]
    out = []
    for e in elements:
        brand = (e.get("tags", {}).get("brand") or "").strip()
        if not brand:
            continue
        lat = e.get("lat") or e.get("center", {}).get("lat")
        lng = e.get("lon") or e.get("center", {}).get("lon")
        if lat is None or lng is None:
            continue
        out.append([round(lat, 5), round(lng, 5), BRANDS.get(brand.lower(), brand)])
    if len(out) < 3000:
        raise SystemExit(f"Only {len(out)} branded stations, not writing.")
    path = os.path.join(os.path.dirname(__file__), "data", "osm_fuel_brands.json")
    json.dump({"source": "© OpenStreetMap contributors, ODbL", "stations": out}, open(path, "w"), separators=(",", ":"))
    print(len(out), "branded stations")


if __name__ == "__main__":
    main()
