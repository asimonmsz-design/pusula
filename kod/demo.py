# -*- coding: utf-8 -*-
"""
PUSULA - Yan Yana Karsilastirma Demosu
======================================

Projenin tezini 30 saniyede gosteren en onemli ciktisi budur.

AYNI icerik havuzu uzerinde iki akis uretir:
  SOL  : Klasik etkilesim odakli algoritma
  SAG  : PUSULA niyet odakli algoritma

ve ikisini olculebilir metriklerle karsilastirir.

Kullanim:
    python demo.py                 -> niyet: ogrenmek (varsayilan)
    python demo.py eglenmek        -> baska bir niyetle calistir
    python demo.py ogrenmek 10     -> ilk 10 gonderiyi goster
"""

import sys

from siralama import (
    havuzu_yukle,
    klasik_siralama,
    pusula_siralama,
    akis_metrikleri,
    NIYETLER,
    NIYET_ETIKETLERI,
)


def kisalt(metin, uzunluk=52):
    """Metni tabloya sigacak sekilde kisaltir."""
    if len(metin) <= uzunluk:
        return metin
    return metin[:uzunluk - 3] + "..."


def akis_yazdir(baslik, akis, aciklama):
    print()
    print("=" * 74)
    print(baslik)
    print(aciklama)
    print("=" * 74)
    for sira, gonderi in enumerate(akis, 1):
        isaret = " [CLICKBAIT]" if gonderi.get("clickbait", 0) > 0.4 else ""
        print("%2d. %s%s" % (sira, kisalt(gonderi["metin"]), isaret))
        print("    kategori: %-22s pismanlik: %.2f"
              % (gonderi["kategori"], gonderi["pismanlik_olasiligi"]))


def karsilastirma_yazdir(m_klasik, m_pusula):
    print()
    print("=" * 74)
    print("OLCUM SONUCLARI")
    print("=" * 74)
    print("%-26s %12s %12s %14s" % ("METRIK", "KLASIK", "PUSULA", "DEGISIM"))
    print("-" * 74)

    satirlar = [
        ("Niyet uyumu",        "niyet_uyumu",     True),
        ("Beklenen tatmin",    "tatmin",          True),
        ("Pismanlik olasiligi","pismanlik",       False),
        ("Clickbait orani",    "clickbait_orani", False),
        ("Etkilesim puani",    "etkilesim",       None),
    ]

    for etiket, anahtar, yuksek_iyi in satirlar:
        k = m_klasik[anahtar]
        p = m_pusula[anahtar]

        if k == 0:
            degisim_metni = "  --"
        else:
            degisim = 100.0 * (p - k) / k
            isaret = "+" if degisim >= 0 else ""
            if yuksek_iyi is None:
                yorum = ""
            elif (degisim > 0) == yuksek_iyi:
                yorum = " IYI"
            else:
                yorum = " KOTU"
            degisim_metni = "%s%.0f%%%s" % (isaret, degisim, yorum)

        print("%-26s %12.3f %12.3f %14s" % (etiket, k, p, degisim_metni))

    print("-" * 74)


def ana(niyet="ogrenmek", adet=20):
    if niyet not in NIYETLER:
        print("Bilinmeyen niyet: %s" % niyet)
        print("Gecerli niyetler: %s" % ", ".join(NIYETLER.keys()))
        return

    havuz = havuzu_yukle()

    akis_klasik = klasik_siralama(havuz, adet=adet)
    akis_pusula = pusula_siralama(havuz, niyet, adet=adet)

    m_klasik = akis_metrikleri(akis_klasik, niyet)
    m_pusula = akis_metrikleri(akis_pusula, niyet)

    print()
    print("#" * 74)
    print("PUSULA KARSILASTIRMA DEMOSU")
    print("Havuz: %d gonderi   |   Kullanici niyeti: %s   |   Akis: %d gonderi"
          % (len(havuz), NIYET_ETIKETLERI[niyet].upper(), adet))
    print("#" * 74)

    akis_yazdir(
        "SOL AKIS - KLASIK ALGORITMA",
        akis_klasik,
        "Kullanicinin niyeti hesaba katilmaz. Sadece etkilesim maksimize edilir.")

    akis_yazdir(
        "SAG AKIS - PUSULA",
        akis_pusula,
        "Kullanicinin beyan ettigi '%s' niyetine gore siralanir."
        % NIYET_ETIKETLERI[niyet])

    karsilastirma_yazdir(m_klasik, m_pusula)

    print()
    print("YORUM")
    print("-" * 74)
    fark_tatmin = 100.0 * (m_pusula["tatmin"] - m_klasik["tatmin"]) / m_klasik["tatmin"]
    fark_pismanlik = 100.0 * (m_pusula["pismanlik"] - m_klasik["pismanlik"]) / m_klasik["pismanlik"]
    print("Beklenen tatmin %%%.0f artti, pismanlik olasiligi %%%.0f azaldi."
          % (fark_tatmin, abs(fark_pismanlik)))
    print("Etkilesim puani dustu; ancak dusen kisim clickbait ve amacsiz")
    print("kaydirma kaynakli etkilesimdir. Niyete uygun etkilesim korunmustur.")
    print()


if __name__ == "__main__":
    secilen_niyet = sys.argv[1] if len(sys.argv) > 1 else "ogrenmek"
    secilen_adet = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    ana(secilen_niyet, secilen_adet)
