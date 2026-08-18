# -*- coding: utf-8 -*-
"""
PUSULA - Web Uygulamasi Ureteci
===============================

sablon.html icindeki /*__VERI__*/ yer tutucusuna gercek icerik havuzunu
enjekte ederek tek dosyalik, calisir bir HTML uygulamasi uretir.

Neden tek dosya? Gosterim sirasinda sunucu kurmak gerekmesin; dosyaya
cift tiklayinca tarayicida acilsin.

Kullanim:
    python uygulama_uret.py
"""

import json
import os
import random
import shutil
import subprocess
import tempfile

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURASI)

KAYNAK_VERI = os.path.join(KOK, "kod", "veri", "etiketli_havuz.json")
SABLON = os.path.join(BURASI, "sablon.html")
CIKTI = os.path.join(BURASI, "pusula.html")

# Her kategoriden kac gonderi alinacak.
# Tum havuzu gommek dosyayi gereksiz buyutur; kategori basina esit
# ornekleme hem dosyayi kucuk tutar hem her niyette yeterli cesitlilik saglar.
KATEGORI_BASINA = 45

random.seed(7)


def veriyi_hazirla():
    with open(KAYNAK_VERI, "r", encoding="utf-8") as f:
        havuz = json.load(f)

    kategoriler = {}
    for g in havuz:
        kategoriler.setdefault(g["kategori"], []).append(g)

    secilen = []
    for kat, liste in kategoriler.items():
        random.shuffle(liste)
        secilen.extend(liste[:KATEGORI_BASINA])

    random.shuffle(secilen)

    # Alan adlarini kisaltiyoruz - dosya boyutu yariya iniyor.
    #   m  = metin       y  = yazar        k  = kategori
    #   n  = niyet vektoru (tahmin)        cb = clickbait puani
    #   et = etkilesim   tz = tazelik      pi = pismanlik olasiligi
    kompakt = []
    for g in secilen:
        kompakt.append({
            "m": g["metin"],
            "y": g["yazar"],
            "k": g["kategori"],
            "n": [round(x, 2) for x in g["tahmin_niyet"]],
            "cb": round(g["clickbait"], 2),
            "et": round(g["etkilesim_puani"], 2),
            "tz": round(g["tazelik"], 2),
            "pi": round(g["pismanlik_olasiligi"], 2),
        })
    return kompakt


def dogrula(html_yolu):
    """Uretilen sayfanin JavaScript'ini syntax kontrolunden gecirir.

    Neden gerekli: bir zamanlar yer tutucu yanlis degistiriliyordu ve geriye
    "[...veri...][]" kaliyordu. Tek bir syntax hatasi tum <script> blogunu
    dusurdugu icin sayfa sessizce bombos aciliyordu - hicbir hata gorunmuyordu.
    Artik boyle bir durumda uretim basarisiz olur.
    """
    node = shutil.which("node")
    if not node:
        print("  Dogrulama      : ATLANDI (node bulunamadi)")
        return

    with open(html_yolu, "r", encoding="utf-8") as f:
        html = f.read()

    if "<script>" not in html:
        raise RuntimeError("Uretilen dosyada <script> blogu yok.")
    js = html.split("<script>", 1)[1].rsplit("</script>", 1)[0]

    gecici = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                         encoding="utf-8")
    try:
        gecici.write(js)
        gecici.close()
        sonuc = subprocess.run([node, "--check", gecici.name],
                               capture_output=True, text=True, encoding="utf-8")
        if sonuc.returncode != 0:
            # Node hatali satirin tamamini basar; veri satiri 90 KB oldugu icin
            # sadece hata mesajini gosteriyoruz.
            satirlar = (sonuc.stderr or "").splitlines()
            ozet = [s for s in satirlar if "Error" in s] or satirlar[-3:]
            raise RuntimeError("Uretilen JavaScript gecersiz:\n  " +
                               "\n  ".join(ozet))
    finally:
        os.unlink(gecici.name)

    print("  Dogrulama      : JavaScript syntax OK")


def uret():
    veri = veriyi_hazirla()

    with open(SABLON, "r", encoding="utf-8") as f:
        sablon = f.read()

    # Yer tutucu "/*__VERI__*/[]" seklinde; bos dizi sablonun kendi basina da
    # gecerli JavaScript kalmasini saglar. Degistirirken bos diziyi de
    # kapsamazsak geriye "[...veri...][]" kalir ve sayfa syntax hatasi verir.
    YER_TUTUCU = "/*__VERI__*/[]"
    if YER_TUTUCU not in sablon:
        raise RuntimeError("sablon.html icinde %s yer tutucusu bulunamadi." % YER_TUTUCU)

    veri_js = json.dumps(veri, ensure_ascii=False, separators=(",", ":"))
    cikti = sablon.replace(YER_TUTUCU, veri_js)

    with open(CIKTI, "w", encoding="utf-8") as f:
        f.write(cikti)

    boyut_kb = os.path.getsize(CIKTI) / 1024
    print("Uygulama uretildi")
    print("  Gonderi sayisi : %d" % len(veri))
    print("  Dosya          : %s" % CIKTI)
    print("  Boyut          : %.0f KB" % boyut_kb)

    kategoriler = {}
    for g in veri:
        kategoriler[g["k"]] = kategoriler.get(g["k"], 0) + 1
    print("  Kategoriler    : %d" % len(kategoriler))

    dogrula(CIKTI)


if __name__ == "__main__":
    uret()
