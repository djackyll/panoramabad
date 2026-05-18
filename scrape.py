#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request
import re
import json
import csv
import os
from datetime import datetime, timezone

URL = "https://bad.dinkelscherben.info/index.php"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8", errors="replace")

def parse(html):
    wasser = re.search(r"Wasser:\s*([\d,\.]+)\s*°C", html)
    luft   = re.search(r"Luft:\s*([\d,\.]+)\s*°C",   html)
    ts     = re.search(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", html)
    return (
        wasser.group(1).replace(",", ".") if wasser else None,
        luft.group(1).replace(",", ".")   if luft   else None,
        ts.group(1)                        if ts     else None,
    )

html = fetch(URL)
wasser, luft, messung_ts = parse(html)
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

data = {
    "abgefragt_utc": now,
    "messung_ts":    messung_ts or "",
    "wasser_c":      float(wasser) if wasser else None,
    "luft_c":        float(luft)   if luft   else None,
}
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Wasser: {wasser} C  |  Luft: {luft} C  |  Messung: {messung_ts}")

file_exists = os.path.isfile("history.csv")
with open("history.csv", "a", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    if not file_exists:
        w.writerow(["abgefragt_utc", "messung_ts", "wasser_c", "luft_c"])
    w.writerow([now, messung_ts or "", wasser or "", luft or ""])
