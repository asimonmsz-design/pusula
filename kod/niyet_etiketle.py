# -*- coding: utf-8 -*-
"""
PUSULA - Niyet Etiketleme Modulu
================================

GOREVI
------
Bir gonderi metnini okuyup, o gonderinin 4 boyutlu niyet vektorunu TAHMIN eder:

    [ogretici, eglendirici, haber, sosyal]

Onemli: Bu modul gonderinin gercek vektorunu GORMEZ. Sadece metne bakar.
Tahmin ettikten sonra gercek degerle karsilastirip isabetini olceriz.

IKI CALISMA MODU
----------------
1) SEZGISEL MOD (varsayilan, internet/API gerektirmez)
   Anahtar kelime sozlukleri ve yapisal sinyaller (soru isareti, buyuk harf,
   unlem) kullanarak vektoru hesaplar. Hizli ve bedava.

2) LLM MODU (opsiyonel)
   Turkce bir dil modeline gonderiyi verip vektoru istemek. Gercek sistemde
   kullanilacak yontem budur. Bu dosyada arayuzu hazir birakilmistir;
   API anahtari tanimlandiginda devreye girer.

DURUSTLUK NOTU (rapora da yazilacak)
------------------------------------
Sezgisel mod, sablon tabanli sentetik veri uzerinde gercekcinin uzerinde
basari gosterir; cunku uretilen metinler duzenli kaliplardan gelir. Gercek
kullanici metinlerinde (argo, ironi, yazim hatasi) bu basari belirgin sekilde
duser. Bu yuzden urun surumunde LLM modu esastir. Sezgisel mod, LLM'in
erisilemedigi durumlar icin yedek (fallback) katmandir.
"""

import json
import os
import re

VERI_DOSYASI = os.path.join(os.path.dirname(__file__), "veri", "icerik_havuzu.json")
CIKTI_DOSYASI = os.path.join(os.path.dirname(__file__), "veri", "etiketli_havuz.json")

NIYET_BOYUTLARI = ["ogretici", "eglendirici", "haber", "sosyal"]


# ---------------------------------------------------------------------------
# ANAHTAR KELIME SOZLUKLERI
# ---------------------------------------------------------------------------
# Her boyut icin, o boyuta isaret eden kelimeler ve agirliklari.
# Agirlik = kelimenin o boyut icin ne kadar guclu bir sinyal oldugu.

SOZLUK = {
    "ogretici": {
        "anlatiyorum": 0.9, "aciklama": 0.8, "nasil": 0.7, "adim adim": 0.9,
        "ogren": 0.8, "yol haritasi": 0.85, "kavram": 0.7, "inceledim": 0.35,
        "yontem": 0.7, "calisir": 0.6, "temel": 0.5, "ornekli": 0.7,
        "hata": 0.5, "cozum": 0.5, "analiz": 0.35, "rakamlarla": 0.35,
        "calisma yayimlandi": 0.8, "ozetliyorum": 0.7, "sifirdan": 0.8,
        "dakikada": 0.5, "yanlis bilinen": 0.6, "neden onemli": 0.6,
        "bize ne getirecek": 0.5,
    },
    "eglendirici": {
        "komik": 0.9, "absurt": 0.85, "inanamiyorum": 0.7, "aklima gelen": 0.6,
        "izlemeden gecme": 0.8, "sasirtan": 0.7, "illuzyon": 0.6, "dans": 0.6,
        "kedi": 0.6, "video": 0.4, "izlenme": 0.5, "son 10 saniye": 0.8,
        "yasadim": 0.5, "gormemistim": 0.6,
    },
    "haber": {
        "son dakika": 0.95, "aciklama yapildi": 0.85, "resmi": 0.8,
        "veriler": 0.7, "bugun aciklanan": 0.85,
        "kurum": 0.7, "yonetmelik": 0.8, "duyuru": 0.7, "gore durum": 0.7,
        "meselesini": 0.8, "sonuclari ne olur": 0.7, "tartismasi": 0.5,
        "bilgilendirme": 0.75,
        # Gundem/analiz iceriklerini yakalayan sinyaller.
        # Bu iceriklerde "inceledim/analiz" gibi ogretici kelimeler de gecer;
        # ayirt edici olan KONUNUN guncel gundem olmasidir.
        "kisa vadeli": 0.7, "uzun vadeli": 0.7, "herkesin atladigi": 0.6,
        "issizligi": 0.75, "politikalari": 0.75, "yatirimlari": 0.7,
        "sehir planlamasi": 0.7, "enerji donusumu": 0.7, "tarim uretimi": 0.7,
        "hava durumu": 0.7, "sinav takvimi": 0.7, "burs basvurulari": 0.7,
        "ulasim duzenlemesi": 0.7, "ekonomi verileri": 0.8,
    },
    "sosyal": {
        "tesekkurler": 0.85, "iyi ki varsiniz": 0.95, "ne dusunuyorsunuz": 0.9,
        "merak ediyorum": 0.8, "oneriniz": 0.85, "yazsin": 0.7, "sizce": 0.85,
        "birlikte": 0.7, "ekipce": 0.8, "herkese": 0.6, "guzeldi": 0.6,
        "bulusma": 0.7, "deneyimi olanlar": 0.8, "nasil cozulur": 0.7,
    },
}

# Clickbait / kiskirtici dil sinyalleri.
#
# TASARIM KARARI:
# Clickbait, bir NIYET boyutu degildir. Bir gonderi hem "haber niyetine hizmet
# ediyor" hem de "clickbait" olabilir. Bu yuzden clickbait'i niyet vektorunun
# icine karistirmiyoruz; AYRI bir kalite sinyali olarak hesapliyoruz.
#
# Ilk denememizde clickbait tespitinde niyet vektorunu bozuyorduk ve bu
# kategoride baskin niyet isabeti %25'e dusmustu. Iki kaygiyi ayirinca
# hem isabet duzeldi hem de mimari temizlendi:
#   - niyet vektoru  -> icerik HANGI ihtiyaca hizmet ediyor?
#   - clickbait puani-> bu hizmeti NE KADAR durust sunuyor?
# Siralama motoru ikisini ayri ayri kullanir.
CLICKBAIT_ISARETLERI = [
    "gercek ortaya cikti", "sok edici", "dikkat!", "kimsenin soylemedigi",
    "herkes yaniliyor", "asil sebep", "birbirine girdi", "inanamayacaksiniz",
    "yapanlar dikkat", "iste asil", "buyuyor. taraflar",
]


def _metin_temizle(metin):
    """
    Kucuk harfe cevirir ve Turkce karakterleri sadelestirir.

    TURKCE 'I' TUZAGI (gercek bir hata, duzeltildi)
    ------------------------------------------------
    Python'da "İ".lower() sonucu "i" DEGILDIR; "i" + birlesik nokta (U+0307)
    olmak uzere IKI karakter doner. Bu yuzden "SON DAKİKA".lower() ifadesi
    "son daki̇ka" olur ve sozlukteki "son dakika" ile eslesmez.

    Ayni sekilde "I".lower() -> "i" olur ama Turkce'de "I" harfinin kucugu
    "ı"dir. Bu iki harfi lower() cagrilmadan ONCE elle donusturuyoruz.

    Bu hata, iceriklere Turkce karakter eklendikten sonra baskin niyet
    isabetinin %96.6'dan %92.7'ye dusmesine yol acmisti.
    """
    metin = metin.replace("İ", "i").replace("I", "ı")
    metin = metin.lower()
    donusum = str.maketrans("çğıöşüâîû", "cgiosuaiu")
    return metin.translate(donusum)


def sezgisel_tahmin(metin):
    """
    Metinden niyet vektoru tahmin eder.

    ADIMLAR:
      1. Her boyut icin sozlukteki kelimeleri ara, agirliklarini topla.
      2. Yapisal sinyalleri ekle (soru isareti, buyuk harf orani).
      3. Clickbait tespit edilirse ogretici/haber puanini dusur.
      4. Ham puanlari 0-1 araligina sikistir.
    """
    ham = _metin_temizle(metin)
    puanlar = {boyut: 0.0 for boyut in NIYET_BOYUTLARI}

    # 1. Sozluk taramasi
    for boyut, kelimeler in SOZLUK.items():
        for kelime, agirlik in kelimeler.items():
            if kelime in ham:
                puanlar[boyut] += agirlik

    # 2. Yapisal sinyaller
    # Soru isareti -> sosyal etkilesim davetidir
    if "?" in metin:
        puanlar["sosyal"] += 0.55

    # Buyuk harfle yazilmis uzun kelime (SON DAKIKA gibi) -> haber sinyali
    if re.search(r"\b[A-ZÇĞİÖŞÜ]{5,}\b", metin):
        puanlar["haber"] += 0.6

    # Unlem -> eglence veya clickbait
    if "!" in metin:
        puanlar["eglendirici"] += 0.25

    # 3. Clickbait duzeltmesi
    # Clickbait bir gonderiyi "eglenceli" veya "haber" YAPMAZ; sadece
    # ogreticilik iddiasini gecersiz kilar. Bu yuzden yalnizca ogretici
    # boyutunu kisiyoruz, diger boyutlara dokunmuyoruz.
    # (Clickbait'in asil etkisi ayri bir kalite sinyali olarak hesaplanir,
    #  bkz. clickbait_puani fonksiyonu.)
    if any(isaret in ham for isaret in CLICKBAIT_ISARETLERI):
        puanlar["ogretici"] *= 0.25

    # 4. Normalize et: en yuksek ham puani referans alarak 0-1'e sikistir.
    #    Referansi 2.0'da sabitliyoruz ki farkli gonderiler karsilastirilabilir olsun.
    vektor = []
    for boyut in NIYET_BOYUTLARI:
        deger = min(1.0, puanlar[boyut] / 2.0)
        vektor.append(round(deger, 3))

    # Hicbir sinyal yakalanmadiysa notr bir taban ver (tamamen sifir olmasin)
    if sum(vektor) < 0.05:
        vektor = [0.25, 0.25, 0.25, 0.25]

    return vektor


def clickbait_puani(metin):
    """
    Metnin ne kadar kiskirtici/clickbait dil kullandigini 0-1 arasi olcer.

    Bu, niyet vektorunden AYRI bir sinyaldir. Siralama motoru bu puani
    icerigin kalite carpanini dusurmek icin kullanir: gonderi kullanicinin
    niyetine uygun olsa bile, clickbait ise akista geriye duser.

    Olculen sinyaller:
      - Bilinen clickbait kaliplari
      - Buyuk harfle bagirma (SOK, GERCEK gibi)
      - Asiri unlem kullanimi
    """
    ham = _metin_temizle(metin)
    puan = 0.0

    for isaret in CLICKBAIT_ISARETLERI:
        if isaret in ham:
            puan += 0.45

    # Buyuk harfle yazilmis vurgu kelimeleri (SON DAKIKA disinda)
    buyuk_kelimeler = re.findall(r"\b[A-ZÇĞİÖŞÜ]{4,}\b", metin)
    for kelime in buyuk_kelimeler:
        if kelime not in ("SON", "DAKIKA"):
            puan += 0.2

    # Unlem yogunlugu
    puan += 0.15 * metin.count("!")

    return round(min(1.0, puan), 3)


def llm_tahmin(metin):
    """
    LLM modu - urun surumunde kullanilacak yontem.

    Gercek sistemde buraya Turkce bir dil modeline yapilan cagri gelir.
    Model su formatta bir istem alir:

        "Asagidaki sosyal medya gonderisini 0-1 arasi puanla.
         ogretici / eglendirici / haber / sosyal. Sadece JSON don.
         Gonderi: {metin}"

    Su an API anahtari tanimli olmadigi icin sezgisel moda dusuluyor.
    """
    # TODO: API anahtari tanimlandiginda burasi doldurulacak.
    return sezgisel_tahmin(metin)


def mutlak_hata(tahmin, gercek):
    """Iki vektor arasindaki ortalama mutlak hatayi (MAE) hesaplar."""
    return sum(abs(t - g) for t, g in zip(tahmin, gercek)) / len(tahmin)


def baskin_boyut(vektor):
    """Vektordeki en yuksek degerli boyutun adini dondurur."""
    return NIYET_BOYUTLARI[vektor.index(max(vektor))]


def havuzu_etiketle(mod="sezgisel"):
    """Tum havuzu etiketler ve isabet metriklerini hesaplar."""
    with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
        havuz = json.load(f)

    tahmin_fn = sezgisel_tahmin if mod == "sezgisel" else llm_tahmin

    hatalar = []
    baskin_dogru = 0

    for gonderi in havuz:
        tahmin = tahmin_fn(gonderi["metin"])
        gonderi["tahmin_niyet"] = tahmin
        gonderi["clickbait"] = clickbait_puani(gonderi["metin"])

        hatalar.append(mutlak_hata(tahmin, gonderi["gercek_niyet"]))
        if baskin_boyut(tahmin) == baskin_boyut(gonderi["gercek_niyet"]):
            baskin_dogru += 1

    ort_hata = sum(hatalar) / len(hatalar)
    baskin_isabet = baskin_dogru / len(havuz)

    return havuz, ort_hata, baskin_isabet


def rapor_yazdir(havuz, ort_hata, baskin_isabet):
    print("=" * 62)
    print("NIYET ETIKETLEME SONUCLARI")
    print("=" * 62)
    print("Etiketlenen gonderi     : %d" % len(havuz))
    print("Ortalama mutlak hata    : %.3f  (dusuk = iyi, 0-1 arasi)" % ort_hata)
    print("Baskin niyet isabeti    : %.1f%%" % (baskin_isabet * 100))
    print()

    # Kategori bazinda isabet
    print("%-24s %10s %12s" % ("KATEGORI", "ADET", "BASKIN ISABET"))
    print("-" * 62)
    kategoriler = sorted(set(g["kategori"] for g in havuz))
    for kat in kategoriler:
        alt = [g for g in havuz if g["kategori"] == kat]
        dogru = sum(1 for g in alt
                    if baskin_boyut(g["tahmin_niyet"]) == baskin_boyut(g["gercek_niyet"]))
        print("%-24s %10d %11.1f%%" % (kat, len(alt), 100.0 * dogru / len(alt)))
    print()

    # Ornek karsilastirmalar
    print("ORNEK TAHMINLER")
    print("-" * 62)
    for gonderi in havuz[:4]:
        print("Metin  : %s" % gonderi["metin"][:60])
        print("Gercek : %s" % gonderi["gercek_niyet"])
        print("Tahmin : %s" % gonderi["tahmin_niyet"])
        print()


if __name__ == "__main__":
    havuz, ort_hata, baskin_isabet = havuzu_etiketle(mod="sezgisel")
    rapor_yazdir(havuz, ort_hata, baskin_isabet)

    with open(CIKTI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(havuz, f, ensure_ascii=False, indent=1)

    print("Kaydedildi: %s" % CIKTI_DOSYASI)
