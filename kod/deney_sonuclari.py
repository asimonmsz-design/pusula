# -*- coding: utf-8 -*-
"""
PUSULA - Deney Sonuclari Ureteci
================================

Tum niyetler icin klasik ve PUSULA akislarini karsilastirir, sonuclari
hem terminale yazdirir hem de rapora yapistirilabilecek bir metin
dosyasina kaydeder.

Kullanim:
    python deney_sonuclari.py
"""

import os

from siralama import (
    havuzu_yukle,
    klasik_siralama,
    pusula_siralama,
    akis_metrikleri,
    NIYETLER,
    NIYET_ETIKETLERI,
)

CIKTI = os.path.join(os.path.dirname(__file__), "veri", "deney_sonuclari.txt")
AKIS_UZUNLUGU = 20


def deneyi_calistir():
    havuz = havuzu_yukle()
    satirlar = []

    def yaz(metin=""):
        print(metin)
        satirlar.append(metin)

    yaz("=" * 78)
    yaz("PUSULA - DENEY SONUCLARI")
    yaz("=" * 78)
    yaz("Icerik havuzu      : %d sentetik Turkce gonderi" % len(havuz))
    yaz("Akis uzunlugu      : ilk %d gonderi" % AKIS_UZUNLUGU)
    yaz("Karsilastirilan    : Klasik (etkilesim odakli) vs PUSULA (niyet odakli)")
    yaz("Adil baseline      : Iki algoritma da ayni cesitlilik kisiti ve")
    yaz("                     temel spam filtresiyle calistirilmistir.")
    yaz()

    basliklar = ("NIYET", "UYUM-K", "UYUM-P", "TATMIN-K", "TATMIN-P",
                 "PISM-K", "PISM-P", "CB-K", "CB-P")
    yaz("%-16s %7s %7s %9s %9s %7s %7s %6s %6s" % basliklar)
    yaz("-" * 78)

    toplamlar = {"tatmin_k": 0.0, "tatmin_p": 0.0,
                 "pism_k": 0.0, "pism_p": 0.0,
                 "uyum_k": 0.0, "uyum_p": 0.0,
                 "cb_k": 0.0, "cb_p": 0.0,
                 "etk_k": 0.0, "etk_p": 0.0}

    for niyet in NIYETLER:
        akis_k = klasik_siralama(havuz, adet=AKIS_UZUNLUGU)
        akis_p = pusula_siralama(havuz, niyet, adet=AKIS_UZUNLUGU)

        mk = akis_metrikleri(akis_k, niyet)
        mp = akis_metrikleri(akis_p, niyet)

        yaz("%-16s %7.3f %7.3f %9.3f %9.3f %7.3f %7.3f %5.0f%% %5.0f%%" % (
            NIYET_ETIKETLERI[niyet],
            mk["niyet_uyumu"], mp["niyet_uyumu"],
            mk["tatmin"], mp["tatmin"],
            mk["pismanlik"], mp["pismanlik"],
            mk["clickbait_orani"] * 100, mp["clickbait_orani"] * 100,
        ))

        toplamlar["uyum_k"] += mk["niyet_uyumu"]
        toplamlar["uyum_p"] += mp["niyet_uyumu"]
        toplamlar["tatmin_k"] += mk["tatmin"]
        toplamlar["tatmin_p"] += mp["tatmin"]
        toplamlar["pism_k"] += mk["pismanlik"]
        toplamlar["pism_p"] += mp["pismanlik"]
        toplamlar["cb_k"] += mk["clickbait_orani"]
        toplamlar["cb_p"] += mp["clickbait_orani"]
        toplamlar["etk_k"] += mk["etkilesim"]
        toplamlar["etk_p"] += mp["etkilesim"]

    n = len(NIYETLER)
    yaz("-" * 78)
    yaz("%-16s %7.3f %7.3f %9.3f %9.3f %7.3f %7.3f %5.0f%% %5.0f%%" % (
        "ORTALAMA",
        toplamlar["uyum_k"] / n, toplamlar["uyum_p"] / n,
        toplamlar["tatmin_k"] / n, toplamlar["tatmin_p"] / n,
        toplamlar["pism_k"] / n, toplamlar["pism_p"] / n,
        toplamlar["cb_k"] / n * 100, toplamlar["cb_p"] / n * 100,
    ))
    yaz()
    yaz("K = Klasik algoritma, P = PUSULA")
    yaz("UYUM   : niyet uyumu (yuksek iyi)")
    yaz("TATMIN : beklenen tatmin = uyum x (1 - pismanlik) (yuksek iyi)")
    yaz("PISM   : ortalama pismanlik olasiligi (dusuk iyi)")
    yaz("CB     : akistaki clickbait orani (dusuk iyi)")
    yaz()

    # Ozet degisimler
    yaz("=" * 78)
    yaz("OZET")
    yaz("=" * 78)

    def degisim(anahtar_k, anahtar_p):
        k = toplamlar[anahtar_k] / n
        p = toplamlar[anahtar_p] / n
        if k == 0:
            return p, k, 0.0
        return p, k, 100.0 * (p - k) / k

    p, k, d = degisim("tatmin_k", "tatmin_p")
    yaz("Beklenen tatmin      : %.3f -> %.3f  (%+.0f%%)" % (k, p, d))
    p, k, d = degisim("pism_k", "pism_p")
    yaz("Pismanlik olasiligi  : %.3f -> %.3f  (%+.0f%%)" % (k, p, d))
    p, k, d = degisim("uyum_k", "uyum_p")
    yaz("Niyet uyumu          : %.3f -> %.3f  (%+.0f%%)" % (k, p, d))
    p, k, d = degisim("cb_k", "cb_p")
    yaz("Clickbait orani      : %.1f%% -> %.1f%%" % (k * 100, p * 100))
    p, k, d = degisim("etk_k", "etk_p")
    yaz("Etkilesim puani      : %.3f -> %.3f  (%+.0f%%)" % (k, p, d))
    yaz()
    yaz("NOT: Bu sonuclar sentetik veri uzerinde alinmistir. Gercek kullanici")
    yaz("verisiyle mutlak degerlerin degismesi beklenir; anlamli olan, iki")
    yaz("algoritma arasindaki YONSEL farktir.")

    return "\n".join(satirlar)


if __name__ == "__main__":
    metin = deneyi_calistir()
    with open(CIKTI, "w", encoding="utf-8") as f:
        f.write(metin)
    print()
    print("Kaydedildi: %s" % CIKTI)
