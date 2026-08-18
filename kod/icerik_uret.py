# -*- coding: utf-8 -*-
"""
PUSULA - Sentetik Icerik Havuzu Ureteci
=======================================

Bu dosya, prototipin uzerinde calisacagi sahte sosyal medya gonderi havuzunu uretir.

NEDEN SENTETIK VERI?
--------------------
Gercek bir platformun gonderi verisine erisimimiz yok. Ayrica gercek kullanici
verisi kullanmak KVKK acisindan izin gerektirirdi. Sentetik veri kullanmak
bize iki avantaj saglar:

  1. Her gonderinin GERCEK niyet vektorunu biliyoruz (ground truth). Boylece
     niyet_etiketle.py'nin ne kadar isabetli calistigini olcebiliyoruz.
  2. Icerik dagilimini kontrol edebiliyoruz (ornegin: havuzun %15'i clickbait
     olsun diyebiliyoruz).

NIYET VEKTORU NEDIR?
--------------------
Her gonderi 4 boyutlu bir vektorle temsil edilir:

    [ogretici, eglendirici, haber, sosyal]

Her boyut 0-1 arasindadir. Ornek:
    Uzun anlatim videosu  -> [0.90, 0.25, 0.10, 0.10]
    Mizah gonderisi       -> [0.10, 0.92, 0.05, 0.35]

Bu, gonderinin hangi kullanici niyetine ne kadar hizmet ettigini gosterir.

IKI KRITIK EK ALAN
------------------
etkilesim_puani   : Klasik (etkilesim odakli) algoritmanin optimize ettigi deger.
                    Tiklama/yorum/paylasim potansiyeli.
pismanlik_olasiligi: Kullanicinin bu icerigi tukettikten sonra "vaktimi bosa
                    harcadim" hissetme olasiligi.

Bu ikisinin ARASINDAKI KOPUKLUK projenin butun tezidir: yuksek etkilesim
ceken icerik cogu zaman yuksek pismanlik da uretir. Klasik algoritma bunu
goremez cunku sadece etkilesime bakar.
"""

import json
import random
import os

# Tekrar uretilebilirlik icin sabit tohum. Ayni veriyi her calistirmada uretir.
random.seed(42)

CIKTI_DOSYASI = os.path.join(os.path.dirname(__file__), "veri", "icerik_havuzu.json")

# Niyet boyutlarinin sirasi. Kod boyunca bu sira degismez.
NIYET_BOYUTLARI = ["ogretici", "eglendirici", "haber", "sosyal"]


# ---------------------------------------------------------------------------
# KATEGORI TANIMLARI
# ---------------------------------------------------------------------------
# Her kategori icin:
#   vektor      : temel niyet vektoru (uretimde uzerine gurultu eklenir)
#   etkilesim   : ortalama etkilesim potansiyeli (0-1)
#   pismanlik   : ortalama pismanlik olasiligi (0-1)
#   oran        : havuzdaki payi
#   sablonlar   : metin uretimi icin kalip cumleler

KATEGORILER = {
    "egitim_anlatim": {
        "vektor": [0.90, 0.25, 0.10, 0.10],
        "etkilesim": 0.35,
        "pismanlik": 0.08,
        "oran": 0.12,
        "yazar": ["Mühendislik Notları", "Ders Defteri", "Anlatarak Öğren",
                  "Kürsü", "Formül ve Ötesi"],
        "sablonlar": [
            "{konu} konusunu 5 dakikada anlatıyorum. Baştan sona örnekli.",
            "{konu} nasıl çalışır? Sıfırdan başlayarak adım adım açıklama.",
            "Üniversitede kimsenin anlatmadığı şekilde {konu}. Uzun anlatım.",
            "{konu} hakkında bilmen gereken 7 temel kavram.",
            "{konu} öğrenmek isteyenler için hazırladığım yol haritası.",
        ],
        "konular": [
            "Fourier dönüşümü", "lineer cebir", "makine öğrenmesi", "termodinamik",
            "veri yapıları", "elektrik devreleri", "olasılık teorisi", "malzeme bilimi",
            "kontrol sistemleri", "akışkanlar mekaniği", "algoritma analizi",
            "istatistiksel çıkarım", "yapay sinir ağları", "sinyal işleme",
        ],
    },
    "nasil_yapilir": {
        "vektor": [0.88, 0.20, 0.05, 0.15],
        "etkilesim": 0.42,
        "pismanlik": 0.10,
        "oran": 0.10,
        "yazar": ["Atölye Günlüğü", "Yaparak Öğrenen", "Tezgâh Başı",
                  "Prototip Defteri", "Uygulamalı"],
        "sablonlar": [
            "{konu} için kullandığım yöntem. Denedim, çalışıyor.",
            "{konu} yaparken en çok yapılan 4 hata ve çözümü.",
            "Adım adım {konu}. Başlangıç seviyesi için.",
            "{konu} konusunda 2 yılda öğrendiklerimi tek yazıda topladım.",
        ],
        "konular": [
            "3B yazıcı kalibrasyonu", "CAD modelleme", "CNC tezgâh ayarı",
            "PCB tasarımı", "drone montajı", "sunum hazırlama", "CV yazma",
            "proje yönetimi", "kod optimizasyonu", "veri temizleme",
        ],
    },
    "bilim_teknoloji": {
        "vektor": [0.80, 0.35, 0.30, 0.12],
        "etkilesim": 0.48,
        "pismanlik": 0.12,
        "oran": 0.08,
        "yazar": ["Bilim Kısaca", "Laboratuvar Notu", "Teknoloji Gündemi",
                  "Araştırma Özeti"],
        "sablonlar": [
            "{konu} alanında yeni bir çalışma yayımlandı. Özetliyorum.",
            "{konu} hakkında çok konuşulan ama yanlış bilinen bir şey var.",
            "{konu}: neden önemli ve bize ne getirecek?",
        ],
        "konular": [
            "kuantum hesaplama", "füzyon enerjisi", "CRISPR", "yapay zekâ güvenliği",
            "uzay teleskopları", "sinir ağı mimarileri", "katı hal bataryaları",
        ],
    },
    "mizah": {
        "vektor": [0.10, 0.92, 0.05, 0.35],
        "etkilesim": 0.72,
        "pismanlik": 0.30,
        "oran": 0.15,
        "yazar": ["kampüs hâlleri", "geç kalan öğrenci", "vize mağduru",
                  "laboratuvar kaçkını", "son sıra"],
        "sablonlar": [
            "{konu} deyince aklıma gelen tek şey.",
            "Bugün {konu} yaşadım, hâlâ inanamıyorum.",
            "{konu} ile ilgili bu kadar komik bir şey görmemiştim.",
            "Kimse konuşmuyor ama {konu} gerçekten absürt.",
        ],
        "konular": [
            "sabah dersleri", "final haftası", "kampüs yemekhanesi", "otobüs beklemek",
            "grup ödevi", "kod hatası", "yazıcı kuyruğu", "sınav sonucu",
            "staj görüşmesi", "asistan hocam",
        ],
    },
    "eglence_video": {
        "vektor": [0.08, 0.90, 0.10, 0.28],
        "etkilesim": 0.78,
        "pismanlik": 0.38,
        "oran": 0.13,
        "yazar": ["Günün Videosu", "Akış TV", "Viral Kutu", "İzle Geç"],
        "sablonlar": [
            "Bu videoyu izlemeden geçme. {konu}",
            "{konu} — son 10 saniye için kal.",
            "3 milyon izlenme almış {konu} videosu.",
        ],
        "konular": [
            "kedi refleksleri", "sokak müzisyeni", "yemek tarifi hızlı çekim",
            "spor hareketi", "dans akımı", "şaşırtan illüzyon",
        ],
    },
    "son_dakika_haber": {
        "vektor": [0.20, 0.05, 0.95, 0.15],
        "etkilesim": 0.68,
        "pismanlik": 0.18,
        "oran": 0.08,
        "yazar": ["Gündem Masası", "Şehir Bülteni", "Kampüs Duyuru",
                  "Haber Akışı"],
        "sablonlar": [
            "SON DAKİKA: {konu} ile ilgili açıklama yapıldı.",
            "{konu} konusunda resmî kurum bilgilendirmesi yayımlandı.",
            "{konu}: bugün açıklanan verilere göre durum.",
        ],
        "konular": [
            "hava durumu uyarısı", "sınav takvimi", "burs başvuruları",
            "ulaşım düzenlemesi", "yeni yönetmelik", "ekonomi verileri",
        ],
    },
    "gundem_analiz": {
        "vektor": [0.50, 0.10, 0.82, 0.22],
        "etkilesim": 0.55,
        "pismanlik": 0.20,
        "oran": 0.07,
        "yazar": ["Veriyle Bakış", "Uzun Yazı", "Analiz Defteri",
                  "Rakamların Dili"],
        "sablonlar": [
            "{konu} meselesini rakamlarla inceledim. Detaylı analiz.",
            "{konu} hakkında herkesin atladığı bir nokta var.",
            "{konu}: kısa vadeli ve uzun vadeli sonuçları ne olur?",
        ],
        "konular": [
            "genç işsizliği", "teknoloji yatırımları", "eğitim politikaları",
            "enerji dönüşümü", "şehir planlaması", "tarım üretimi",
        ],
    },
    "arkadas_paylasimi": {
        "vektor": [0.12, 0.40, 0.05, 0.90],
        "etkilesim": 0.45,
        "pismanlik": 0.09,
        "oran": 0.12,
        "yazar": ["Elif", "Mert", "Zeynep", "Kerem", "Ayşe", "Burak",
                  "Selin", "Emre"],
        "sablonlar": [
            "Bugün {konu}. İyi ki varsınız.",
            "{konu} için herkese teşekkürler.",
            "Uzun zamandır {konu} yapmamıştık. Güzeldi.",
        ],
        "konular": [
            "ekipçe buluşma", "mezuniyet", "doğum günü", "proje teslimi",
            "kamp dönüşü", "takım antrenmanı", "atölye günü",
        ],
    },
    "soru_tartisma": {
        "vektor": [0.38, 0.25, 0.15, 0.80],
        "etkilesim": 0.62,
        "pismanlik": 0.16,
        "oran": 0.08,
        "yazar": ["Deniz", "Onur", "Ceren", "Yiğit", "Naz", "Barış"],
        "sablonlar": [
            "{konu} konusunda ne düşünüyorsunuz? Gerçekten merak ediyorum.",
            "{konu} için öneriniz var mı? Deneyimi olanlar yazsın.",
            "Sizce {konu} nasıl çözülür?",
        ],
        "konular": [
            "bölüm seçimi", "yurt dışı yüksek lisans", "ilk iş deneyimi",
            "girişim kurma", "takım çalışması", "zaman yönetimi",
        ],
    },
    "clickbait_kiskirtici": {
        # Projenin tezini gosteren kritik kategori:
        # Yuksek etkilesim, YUKSEK pismanlik, dusuk gercek deger.
        "vektor": [0.06, 0.30, 0.45, 0.25],
        "etkilesim": 0.88,
        "pismanlik": 0.72,
        "oran": 0.07,
        "yazar": ["Trend Merkez", "Gündem Şok", "Bunu Gördünüz mü?",
                  "Viral Haber"],
        "sablonlar": [
            "{konu} hakkında kimsenin söylemediği GERÇEK ortaya çıktı!",
            "{konu} yapanlar dikkat! Sonuçları şok edici.",
            "Herkes {konu} konusunda yanılıyor. İşte asıl sebep.",
            "{konu} tartışması büyüyor. Taraflar birbirine girdi.",
        ],
        "konular": [
            "bu alışkanlık", "o meşhur yöntem", "bilinen bir marka",
            "popüler bir tartışma", "yeni çıkan ürün",
        ],
    },
}


def gurultu_ekle(vektor, siddet=0.08):
    """
    Temel kategori vektorune rastgele kucuk sapmalar ekler.

    Neden? Ayni kategorideki her gonderi birebir ayni vektore sahip olsaydi
    veri gercekci olmazdi ve siralama motoru anlamsiz derecede kolay is
    yapardi. Gurultu, gercek dunyadaki cesitliligi taklit eder.

    Sonuc her zaman 0-1 araliginda kalir.
    """
    yeni = []
    for deger in vektor:
        sapma = random.uniform(-siddet, siddet)
        yeni.append(round(min(1.0, max(0.0, deger + sapma)), 3))
    return yeni


def skor_gurultu(temel, siddet=0.12):
    """Etkilesim ve pismanlik puanlarina gurultu ekler."""
    return round(min(1.0, max(0.0, temel + random.uniform(-siddet, siddet))), 3)


def havuz_uret(toplam=2000):
    """
    Belirtilen sayida gonderi uretir.

    Her kategoriden, tanimli 'oran' degeri kadar gonderi uretilir.
    Ornek: mizah orani 0.15 ise 2000 gonderinin ~300'u mizah olur.
    """
    gonderiler = []
    gonderi_id = 1

    for kategori_adi, ayar in KATEGORILER.items():
        adet = int(toplam * ayar["oran"])

        for _ in range(adet):
            sablon = random.choice(ayar["sablonlar"])
            konu = random.choice(ayar["konular"])
            metin = sablon.format(konu=konu)

            gonderiler.append({
                "id": gonderi_id,
                "metin": metin,
                "yazar": random.choice(ayar["yazar"]),
                "kategori": kategori_adi,
                # Gercek niyet vektoru (ground truth).
                # niyet_etiketle.py bunu BILMEDEN tahmin etmeye calisacak.
                "gercek_niyet": gurultu_ekle(ayar["vektor"]),
                "etkilesim_puani": skor_gurultu(ayar["etkilesim"]),
                "pismanlik_olasiligi": skor_gurultu(ayar["pismanlik"]),
                "tazelik": round(random.uniform(0.0, 1.0), 3),
            })
            gonderi_id += 1

    random.shuffle(gonderiler)
    return gonderiler


def ozet_yazdir(gonderiler):
    """Uretilen havuzun dagilimini terminale yazdirir."""
    print("=" * 62)
    print("ICERIK HAVUZU URETILDI")
    print("=" * 62)
    print("Toplam gonderi: %d" % len(gonderiler))
    print()
    print("%-24s %6s %12s %12s" % ("KATEGORI", "ADET", "ETKILESIM", "PISMANLIK"))
    print("-" * 62)

    for kategori_adi in KATEGORILER:
        alt = [g for g in gonderiler if g["kategori"] == kategori_adi]
        if not alt:
            continue
        ort_etkilesim = sum(g["etkilesim_puani"] for g in alt) / len(alt)
        ort_pismanlik = sum(g["pismanlik_olasiligi"] for g in alt) / len(alt)
        print("%-24s %6d %12.2f %12.2f" % (
            kategori_adi, len(alt), ort_etkilesim, ort_pismanlik))

    print("-" * 62)
    genel_etkilesim = sum(g["etkilesim_puani"] for g in gonderiler) / len(gonderiler)
    genel_pismanlik = sum(g["pismanlik_olasiligi"] for g in gonderiler) / len(gonderiler)
    print("%-24s %6d %12.2f %12.2f" % ("GENEL", len(gonderiler),
                                        genel_etkilesim, genel_pismanlik))
    print()


if __name__ == "__main__":
    havuz = havuz_uret(2000)
    ozet_yazdir(havuz)

    os.makedirs(os.path.dirname(CIKTI_DOSYASI), exist_ok=True)
    with open(CIKTI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(havuz, f, ensure_ascii=False, indent=1)

    print("Kaydedildi: %s" % CIKTI_DOSYASI)
