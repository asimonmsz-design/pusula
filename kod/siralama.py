# -*- coding: utf-8 -*-
"""
PUSULA - Siralama Motoru
========================

Bu dosya projenin kalbidir. Iki farkli siralama stratejisini yan yana
uygulanabilir hale getirir:

  1) klasik_siralama()  : Bugunku sosyal medya platformlarinin yaptigi is.
                          Etkilesim potansiyelini maksimize eder.
  2) pusula_siralama()  : Bizim onerimiz.
                          Kullanicinin BEYAN ETTIGI niyete uyumu maksimize eder.

Ikisini ayni icerik havuzu uzerinde calistirip sonuclari karsilastirdigimizda
projenin tezi olculebilir hale gelir.

SIKCA SORULAN: "Etkilesimi tamamen yok mu sayiyorsunuz?"
------------------------------------------------------
Hayir. PUSULA formulunde etkilesim %15 agirlikla YER ALIR. Fark su:
klasik sistemde etkilesim BIRINCIL hedeftir; PUSULA'da ikincil bir
sinyaldir. Amac etkilesimi yok etmek degil, onu tek hakem olmaktan
cikarmaktir.
"""

import json
import math
import os

VERI_DOSYASI = os.path.join(os.path.dirname(__file__), "veri", "etiketli_havuz.json")

NIYET_BOYUTLARI = ["ogretici", "eglendirici", "haber", "sosyal"]


# ---------------------------------------------------------------------------
# KULLANICI NIYET VEKTORLERI
# ---------------------------------------------------------------------------
# Niyet Kapisi ekranindaki her secenek, bir hedef vektore karsilik gelir.
# Degerler tam 0/1 degil; cunku "ogrenmek" isteyen biri arada bir eglenceli
# icerik de gormek ister. Sifir vermek akisi asiri tek tip yapardi.

NIYETLER = {
    "ogrenmek":       [1.00, 0.15, 0.15, 0.05],
    "eglenmek":       [0.10, 1.00, 0.05, 0.25],
    "haberdar_olmak": [0.20, 0.05, 1.00, 0.10],
    "sosyallesmek":   [0.10, 0.30, 0.05, 1.00],
    "dolasmak":       [0.40, 0.55, 0.40, 0.45],
}

NIYET_ETIKETLERI = {
    "ogrenmek": "Ogrenmek",
    "eglenmek": "Eglenmek",
    "haberdar_olmak": "Haberdar olmak",
    "sosyallesmek": "Sosyallesmek",
    "dolasmak": "Sadece dolasmak",
}


def kosinus_benzerligi(a, b):
    """
    Iki vektor arasindaki kosinus benzerligini hesaplar (0-1 arasi).

    NEDEN KOSINUS?
    Nokta carpimi kullansaydik, her boyutta yuksek puan alan "her seye biraz
    uyan" icerikler haksiz avantaj kazanirdi. Kosinus benzerligi vektorlerin
    BUYUKLUGUNU degil YONUNU karsilastirir; yani "bu icerik hangi ihtiyaca
    hizmet ediyor" sorusunu, "ne kadar yogun" sorusundan ayirir.
    """
    nokta = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return nokta / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# 1) KLASIK SIRALAMA - bugunku platformlarin yaptigi
# ---------------------------------------------------------------------------

def klasik_skor(gonderi):
    """
    Etkilesim odakli skor.

    Formul:  0.70 * etkilesim + 0.20 * tazelik + 0.10 * spam_filtresi

    ADIL KARSILASTIRMA NOTU (onemli)
    ---------------------------------------------------
    Ilk denememizde klasik algoritmayi "sadece etkilesim" olarak modellemistik.
    Sonuc: akisin ilk 10 gonderisinin %100'u clickbait cikti. Bu, gercek
    platformlari haksiz sekilde kotu gosteren bir kurgudur; cunku gercek
    platformlar da:
      - temel spam/clickbait filtreleri uygular,
      - akista kategori cesitliligi saglar.

    Bu yuzden klasik baseline'a da ayni iki mekanizmayi verdik. PUSULA'nin
    gosterdigi ustunluk artik ZAYIF bir rakibe karsi degil, makul bir
    rakibe karsi olculuyor. Bu, sonuclari daha az carpici ama cok daha
    savunulabilir kilar.
    """
    spam_filtresi = 1.0 - gonderi.get("clickbait", 0.0)
    return (0.70 * gonderi["etkilesim_puani"]
            + 0.20 * gonderi["tazelik"]
            + 0.10 * spam_filtresi)


def klasik_siralama(havuz, adet=20, cesitlilik_siniri=5):
    """
    Havuzu etkilesim skoruna gore siralar.

    PUSULA ile ayni cesitlilik kisitini uygular; tek fark skor formuludur.
    Boylece iki akis arasindaki fark yalnizca "neyi optimize ettikleri"nden
    kaynaklanir, kisitlardan degil.
    """
    puanli = sorted(havuz, key=klasik_skor, reverse=True)

    secilenler = []
    kategori_sayaci = {}

    for gonderi in puanli:
        if len(secilenler) >= adet:
            break
        kat = gonderi["kategori"]
        if kategori_sayaci.get(kat, 0) >= cesitlilik_siniri:
            continue
        secilenler.append(gonderi)
        kategori_sayaci[kat] = kategori_sayaci.get(kat, 0) + 1

    return secilenler


# ---------------------------------------------------------------------------
# 2) PUSULA SIRALAMA - bizim onerimiz
# ---------------------------------------------------------------------------

# Formuldeki agirliklar. Toplami 1.0'dir.
AGIRLIK_NIYET     = 0.70   # kullanicinin beyan ettigi niyete uyum
AGIRLIK_TAZELIK   = 0.15   # guncellik
AGIRLIK_ETKILESIM = 0.15   # etkilesim (ikincil sinyal olarak korunur)


def pusula_skor(gonderi, niyet_vektoru):
    """
    Niyet odakli skor.

    Formul:
        ( 0.70 * niyet_uyumu + 0.15 * tazelik + 0.15 * etkilesim ) * kalite

    KALITE NEDEN CARPAN? (tasarim karari)
    -------------------------------------------------------
    Ilk versiyonda kalite toplamsal bir terimdi (+0.20 * kalite). Olcum
    sonucunda "eglenmek" niyetinde akisin %25'inin hala clickbait oldugunu
    gorduk: cunku clickbait bir gonderi niyet uyumundan yeterince puan
    toplayip kalite cezasini telafi edebiliyordu.

    Bu yanlisti. Kalite bir BONUS degil, bir KAPIDIR: durust olmayan bir
    icerik, kullanicinin niyetine ne kadar uyarsa uysun one cikmamalidir.
    Carpimsal yapida clickbait=0.95 olan bir gonderinin skoru 0.05 ile
    carpilir ve pratikte akistan duser.

    kalite = 1 - clickbait_puani
    """
    uyum = kosinus_benzerligi(gonderi["tahmin_niyet"], niyet_vektoru)
    kalite = 1.0 - gonderi.get("clickbait", 0.0)

    taban = (AGIRLIK_NIYET * uyum
             + AGIRLIK_TAZELIK * gonderi["tazelik"]
             + AGIRLIK_ETKILESIM * gonderi["etkilesim_puani"])

    return taban * kalite


def pusula_siralama(havuz, niyet_adi, adet=20, cesitlilik_siniri=5):
    """
    Havuzu niyet uyumuna gore siralar.

    CESITLILIK KISITI
    -----------------
    Sadece skora gore siralarsak akis tek tip olur (ornegin 20 gonderinin
    hepsi egitim videosu). Bu filtre balonu yaratir ve kullaniciyi sikar.
    Bu yuzden ayni kategoriden pes pese en fazla 'cesitlilik_siniri' kadar
    gonderi alinmasina izin verilir; sinir dolunca sonraki en iyi FARKLI
    kategoriden gonderi secilir.
    """
    if niyet_adi not in NIYETLER:
        raise ValueError("Bilinmeyen niyet: %s" % niyet_adi)

    niyet_vektoru = NIYETLER[niyet_adi]

    puanli = sorted(havuz,
                    key=lambda g: pusula_skor(g, niyet_vektoru),
                    reverse=True)

    secilenler = []
    kategori_sayaci = {}

    for gonderi in puanli:
        if len(secilenler) >= adet:
            break
        kat = gonderi["kategori"]
        if kategori_sayaci.get(kat, 0) >= cesitlilik_siniri:
            continue
        secilenler.append(gonderi)
        kategori_sayaci[kat] = kategori_sayaci.get(kat, 0) + 1

    # Cesitlilik kisiti yuzunden liste dolmadiysa kalanlari sirayla ekle
    if len(secilenler) < adet:
        for gonderi in puanli:
            if gonderi not in secilenler:
                secilenler.append(gonderi)
            if len(secilenler) >= adet:
                break

    return secilenler


# ---------------------------------------------------------------------------
# OLCUM FONKSIYONLARI
# ---------------------------------------------------------------------------

def akis_metrikleri(akis, niyet_adi):
    """
    Bir akisin kalitesini olcen metrikleri hesaplar.

    Donen degerler:
      niyet_uyumu     : Akistaki gonderilerin niyete ortalama uyumu (0-1)
      pismanlik       : Ortalama pismanlik olasiligi (0-1, dusuk = iyi)
      clickbait_orani : Akistaki clickbait gonderi yuzdesi
      etkilesim       : Ortalama etkilesim puani
      tatmin          : Beklenen tatmin = uyum * (1 - pismanlik)
    """
    niyet_vektoru = NIYETLER[niyet_adi]

    uyumlar = [kosinus_benzerligi(g["tahmin_niyet"], niyet_vektoru) for g in akis]
    pismanliklar = [g["pismanlik_olasiligi"] for g in akis]
    etkilesimler = [g["etkilesim_puani"] for g in akis]
    clickbaitler = [1 for g in akis if g.get("clickbait", 0) > 0.4]

    ort_uyum = sum(uyumlar) / len(akis)
    ort_pismanlik = sum(pismanliklar) / len(akis)

    return {
        "niyet_uyumu": ort_uyum,
        "pismanlik": ort_pismanlik,
        "clickbait_orani": len(clickbaitler) / len(akis),
        "etkilesim": sum(etkilesimler) / len(akis),
        "tatmin": ort_uyum * (1.0 - ort_pismanlik),
    }


def havuzu_yukle():
    """Etiketlenmis icerik havuzunu diskten okur."""
    with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    havuz = havuzu_yukle()
    print("Havuz yuklendi: %d gonderi" % len(havuz))
    print()

    for niyet in NIYETLER:
        akis = pusula_siralama(havuz, niyet, adet=20)
        m = akis_metrikleri(akis, niyet)
        print("%-16s uyum=%.3f  pismanlik=%.3f  tatmin=%.3f"
              % (niyet, m["niyet_uyumu"], m["pismanlik"], m["tatmin"]))
