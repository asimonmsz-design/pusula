# -*- coding: utf-8 -*-
"""
PUSULA - Kontrast Olcumu
========================

Tasarim sistemindeki renk ciftlerinin WCAG 2.1 kontrast oranlarini hesaplar.

Neden var: renkler goze hos geldigi icin secilmisti, olculmemisti.
"Erisilebilirlik degerlendirmesi" sartnamede istenen bir teslimat ve
olculmemis renk secimiyle o dokuman yazilamaz.

Esikler (WCAG 2.1):
  AA  normal metin  : 4.5:1
  AA  buyuk metin   : 3.0:1   (>=18.66px kalin veya >=24px)
  AA  arayuz ogesi  : 3.0:1   (kenarlik, ikon, durum gostergesi)
  AAA normal metin  : 7.0:1

Kullanim:
    python kontrast_olc.py
"""

import sys

# Tasarim jetonlari - sablon.html icindeki :root degerleriyle ayni olmali.
ACIK = {
    "zemin": "#ECF2F2", "yuzey": "#FFFFFF", "yuzey-alt": "#F5FAFA",
    "murekkep": "#0E2226", "sonuk": "#4E6A6E", "cizgi": "#CFE0E0",
    "aksan": "#0A6E76", "aksan-acik": "#DAF0F1", "aksan-ustu": "#FFFFFF",
    "kor": "#A32E22", "kor-acik": "#FBE6E3",
    "iyi": "#0A7A6C", "uyari": "#A32E22", "kotu": "#B0281A",
}

KOYU = {
    "zemin": "#06171A", "yuzey": "#0D2226", "yuzey-alt": "#132C31",
    "murekkep": "#DDECED", "sonuk": "#8DA9AC", "cizgi": "#1E3B41",
    "aksan": "#3FC8D4", "aksan-acik": "#0E353B", "aksan-ustu": "#06171A",
    "kor": "#F08272", "kor-acik": "#3A1D19",
    "iyi": "#3ECBB4", "uyari": "#F08272", "kotu": "#FF7A66",
}

# (aciklama, on renk, arka renk, gereken oran, tur)
CIFTLER = [
    ("Gövde metni",                 "murekkep",  "zemin",      4.5, "metin"),
    ("Kart içi metin",              "murekkep",  "yuzey",      4.5, "metin"),
    ("İkincil metin (aciklama)",    "sonuk",     "yuzey",      4.5, "metin"),
    ("İkincil metin (zeminde)",     "sonuk",     "zemin",      4.5, "metin"),
    ("Etiket / kart alt yazisi",    "sonuk",     "yuzey-alt",  4.5, "metin"),
    ("Aksan metin (baglantilar)",   "aksan",     "yuzey",      4.5, "metin"),
    ("Aksan metin (aksan zemin)",   "aksan",     "aksan-acik", 4.5, "metin"),
    ("Birincil buton yazisi",       "aksan-ustu","aksan",      4.5, "metin"),
    ("Clickbait rozeti",            "uyari",     "kor-acik",   4.5, "metin"),
    # Kenarlik dekoratiftir (WCAG 1.4.11 muaf): durum bildirmez ve yuzeyler
    # arka plan farkiyla da ayirt edilir. Olculur ama esige tabi degildir.
    ("Kenarlik / ayirici (dekoratif)", "cizgi",  "yuzey",      1.0, "dekoratif"),
    ("Zaman halkasi dolgusu",       "aksan",     "yuzey",      3.0, "arayuz"),
    ("Pismanlik cubugu (kor)",      "kor",       "yuzey-alt",  3.0, "arayuz"),
    ("Iyi durum gostergesi",        "iyi",       "yuzey",      3.0, "arayuz"),
    ("Kotu durum gostergesi",       "kotu",      "yuzey",      3.0, "arayuz"),
]


def _kanal(d):
    d = d / 255.0
    return d / 12.92 if d <= 0.04045 else ((d + 0.055) / 1.055) ** 2.4


def parlaklik(hex_renk):
    h = hex_renk.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return 0.2126 * _kanal(r) + 0.7152 * _kanal(g) + 0.0722 * _kanal(b)


def oran(renk1, renk2):
    a, b = parlaklik(renk1), parlaklik(renk2)
    if a < b:
        a, b = b, a
    return (a + 0.05) / (b + 0.05)


def tema_olc(ad, jetonlar):
    print("=" * 74)
    print("%s TEMA" % ad.upper())
    print("=" * 74)
    print("%-30s %-22s %7s %7s  %s" % ("Kullanim", "Renk cifti", "Oran", "Gerek", "Sonuc"))
    print("-" * 74)

    kalanlar = []
    for aciklama, on, arka, gerek, tur in CIFTLER:
        o = oran(jetonlar[on], jetonlar[arka])
        gecti = o >= gerek
        if not gecti:
            kalanlar.append((aciklama, on, arka, o, gerek))
        print("%-30s %-22s %6.2f: %6.1f:  %s"
              % (aciklama, "%s / %s" % (on, arka), o, gerek,
                 "GECER" if gecti else "KALDI"))
    print()
    return kalanlar


def calistir():
    hepsi = []
    hepsi += [("Acik",) + k for k in tema_olc("Acik", ACIK)]
    hepsi += [("Koyu",) + k for k in tema_olc("Koyu", KOYU)]

    print("=" * 74)
    if not hepsi:
        print("SONUC: Tum renk ciftleri WCAG 2.1 AA esigini geciyor.")
        return 0

    print("SONUC: %d cift esigin altinda." % len(hepsi))
    for tema, aciklama, on, arka, o, gerek in hepsi:
        print("  %s tema / %s: %s uzerinde %s = %.2f:1 (gereken %.1f:1)"
              % (tema, aciklama, arka, on, o, gerek))
    return 1


if __name__ == "__main__":
    sys.exit(calistir())
