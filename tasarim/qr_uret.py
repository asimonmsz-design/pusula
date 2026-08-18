# -*- coding: utf-8 -*-
"""
Anket bağlantısı için QR kod ve dağıtım görselleri üretir.

Kullanım:
    python qr_uret.py "https://forms.gle/XXXXXXXX"

Üretilenler (tasarim/qr/ klasörüne):
    anket-qr.png          — sade QR, arka planı beyaz, baskıya uygun
    anket-slayt.png       — 1920x1080, projeksiyon/ekrana yansıtmak için
    anket-afis.png        — A5 oranında afiş (pano, sınıf, kampüs)
    anket-hikaye.png      — 1080x1920 Instagram hikâyesi

Not: QR hata düzeltme seviyesi Q (%25). Kâğıt kırışsa, üstüne bir şey
düşse ya da baskı kalitesi düşük olsa bile okunur. Ekran görüntüsü
alınıp küçültülen QR'lar en çok bu yüzden bozulur.
"""

import sys
import os
import qrcode
from qrcode.constants import ERROR_CORRECT_Q
from PIL import Image, ImageDraw, ImageFont

# --- Renkler: prototipin paletiyle aynı (tasarim/pusula.html) ---
LACIVERT = (13, 27, 42)
BEYAZ = (255, 255, 255)
ACIK_GRI = (168, 178, 190)
TURKUAZ = (64, 201, 190)

CIKIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qr")


def yazi_tipi(boyut, kalin=False):
    """Windows sistem fontu; Türkçe karakterleri destekleyeni seçer."""
    adaylar = ["segoeuib.ttf", "arialbd.ttf"] if kalin else ["segoeui.ttf", "arial.ttf"]
    for ad in adaylar:
        yol = os.path.join("C:\\Windows\\Fonts", ad)
        if os.path.exists(yol):
            return ImageFont.truetype(yol, boyut)
    return ImageFont.load_default()


def qr_uret(url, modul_px=20, kenar=2):
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_Q,
        box_size=modul_px,
        border=kenar,
    )
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB"), qr.version


def ortala_yaz(cizim, y, metin, font, renk, genislik):
    kutu = cizim.textbbox((0, 0), metin, font=font)
    x = (genislik - (kutu[2] - kutu[0])) // 2
    cizim.text((x, y), metin, font=font, fill=renk)
    return y + (kutu[3] - kutu[1])


def afis_uret(qr_img, dosya, en=1748, boy=2480):
    """A5 @ 300dpi. Beyaz zemin — mürekkep tasarrufu ve QR kontrastı için."""
    tuval = Image.new("RGB", (en, boy), BEYAZ)
    ciz = ImageDraw.Draw(tuval)

    ciz.rectangle([0, 0, en, 26], fill=TURKUAZ)

    y = 210
    y = ortala_yaz(ciz, y, "Sosyal medya kullanım", yazi_tipi(112, True), LACIVERT, en) + 60
    y = ortala_yaz(ciz, y, "alışkanlıkları anketi", yazi_tipi(112, True), LACIVERT, en) + 90
    y = ortala_yaz(ciz, y, "4–5 dakika  ·  anonim", yazi_tipi(64), (90, 100, 112), en) + 130

    qr_boy = 1000
    qr_yerlestir = qr_img.resize((qr_boy, qr_boy), Image.LANCZOS)
    tuval.paste(qr_yerlestir, ((en - qr_boy) // 2, y))
    y += qr_boy + 90

    y = ortala_yaz(ciz, y, "Kamerayı QR koda tutmanız yeterli", yazi_tipi(58), (90, 100, 112), en) + 120
    ortala_yaz(ciz, y, "TEKNOFEST öğrenci projesi", yazi_tipi(48), ACIK_GRI, en)

    tuval.save(dosya)
    return dosya


def slayt_uret(qr_img, dosya, en=1920, boy=1080):
    """Projeksiyon / ekran. Beyaz zemin + siyah QR: kamera en kolay bunu okur.

    QR ekran yüksekliğinin %72'si kadar — arka sıradaki telefon da okuyabilsin.
    Yanı metin, altı boş: projeksiyon perdesinin alt kenarı çoğu salonda
    öndeki kafalar tarafından kapatılır, kritik bilgi oraya konmaz.
    """
    tuval = Image.new("RGB", (en, boy), BEYAZ)
    ciz = ImageDraw.Draw(tuval)

    ciz.rectangle([0, 0, en, 18], fill=TURKUAZ)

    qr_boy = 780
    qr_x, qr_y = 130, (boy - qr_boy) // 2
    tuval.paste(qr_img.resize((qr_boy, qr_boy), Image.LANCZOS), (qr_x, qr_y))

    mx = qr_x + qr_boy + 130
    y = 250
    ciz.text((mx, y), "Sosyal medya", font=yazi_tipi(84, True), fill=LACIVERT)
    ciz.text((mx, y + 100), "kullanım anketi", font=yazi_tipi(84, True), fill=LACIVERT)
    ciz.text((mx, y + 250), "Kameranı QR koda tut", font=yazi_tipi(50), fill=(90, 100, 112))
    ciz.text((mx, y + 320), "4–5 dakika  ·  anonim", font=yazi_tipi(50), fill=(90, 100, 112))
    ciz.text((mx, y + 470), "TEKNOFEST öğrenci projesi", font=yazi_tipi(36), fill=ACIK_GRI)

    tuval.save(dosya)
    return dosya


def hikaye_uret(qr_img, dosya, en=1080, boy=1920):
    """Instagram hikâyesi. QR beyaz bir kart üzerinde — koyu zeminde QR okunmaz."""
    tuval = Image.new("RGB", (en, boy), LACIVERT)
    ciz = ImageDraw.Draw(tuval)

    y = 380
    y = ortala_yaz(ciz, y, "Sosyal medya anketi", yazi_tipi(76, True), BEYAZ, en) + 46
    y = ortala_yaz(ciz, y, "4–5 dakika · anonim", yazi_tipi(44), TURKUAZ, en) + 110

    kart = 720
    qr_boy = 620
    kx = (en - kart) // 2
    ciz.rounded_rectangle([kx, y, kx + kart, y + kart], radius=36, fill=BEYAZ)
    tuval.paste(qr_img.resize((qr_boy, qr_boy), Image.LANCZOS),
                (kx + (kart - qr_boy) // 2, y + (kart - qr_boy) // 2))
    y += kart + 100

    y = ortala_yaz(ciz, y, "Ekran görüntüsü al, kameraya tut", yazi_tipi(40), ACIK_GRI, en) + 80
    ortala_yaz(ciz, y, "TEKNOFEST öğrenci projesi", yazi_tipi(34), (110, 122, 138), en)

    tuval.save(dosya)
    return dosya


def main():
    if len(sys.argv) < 2:
        print("Kullanım: python qr_uret.py \"https://forms.gle/...\"")
        return 1

    url = sys.argv[1].strip()
    if not url.startswith("http"):
        print("HATA: bağlantı http:// veya https:// ile başlamalı. Verilen:", url)
        return 1

    os.makedirs(CIKIS, exist_ok=True)
    qr_img, surum = qr_uret(url)

    sade = os.path.join(CIKIS, "anket-qr.png")
    qr_img.save(sade)

    slayt = slayt_uret(qr_img, os.path.join(CIKIS, "anket-slayt.png"))
    afis = afis_uret(qr_img, os.path.join(CIKIS, "anket-afis.png"))
    hikaye = hikaye_uret(qr_img, os.path.join(CIKIS, "anket-hikaye.png"))

    print("Bağlantı  :", url)
    print("QR sürümü :", surum, "(%d modül, hata düzeltme: Q %%25)" % (surum * 4 + 17))
    print()
    for yol in (sade, slayt, afis, hikaye):
        print("  %-18s %6.1f KB   %s" % (os.path.basename(yol),
                                         os.path.getsize(yol) / 1024,
                                         Image.open(yol).size))
    print("\nKlasör:", CIKIS)
    print("\nBASMADAN ÖNCE: telefonunla QR'ı okut, formun açıldığını doğrula.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
