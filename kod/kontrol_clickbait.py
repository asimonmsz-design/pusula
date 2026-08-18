# -*- coding: utf-8 -*-
"""Clickbait tespitinin kategori bazinda ne kadar isabetli oldugunu olcer."""

import json
import os

VERI = os.path.join(os.path.dirname(__file__), "veri", "etiketli_havuz.json")

with open(VERI, "r", encoding="utf-8") as f:
    havuz = json.load(f)

print("%-24s %8s %14s %14s" % ("KATEGORI", "ADET", "ORT.CLICKBAIT", "ESIK>0.4 ORANI"))
print("-" * 66)

for kat in sorted(set(g["kategori"] for g in havuz)):
    alt = [g for g in havuz if g["kategori"] == kat]
    ort = sum(g["clickbait"] for g in alt) / len(alt)
    yakalanan = sum(1 for g in alt if g["clickbait"] > 0.4) / len(alt)
    print("%-24s %8d %14.3f %13.1f%%" % (kat, len(alt), ort, yakalanan * 100))

print()
cb = [g for g in havuz if g["kategori"] == "clickbait_kiskirtici"]
digerleri = [g for g in havuz if g["kategori"] != "clickbait_kiskirtici"]

dogru_pozitif = sum(1 for g in cb if g["clickbait"] > 0.4)
yanlis_pozitif = sum(1 for g in digerleri if g["clickbait"] > 0.4)

print("Clickbait tespiti (esik 0.4):")
print("  Duyarlilik (recall)  : %.1f%%  (%d/%d clickbait yakalandi)"
      % (100.0 * dogru_pozitif / len(cb), dogru_pozitif, len(cb)))
print("  Yanlis alarm         : %.1f%%  (%d/%d masum gonderi yanlis isaretlendi)"
      % (100.0 * yanlis_pozitif / len(digerleri), yanlis_pozitif, len(digerleri)))
