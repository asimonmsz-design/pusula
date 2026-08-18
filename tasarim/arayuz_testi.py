# -*- coding: utf-8 -*-
"""
PUSULA - Arayuz Testi
=====================

Uygulamanin TUM ekranlarini sahte bir DOM uzerinde cizer ve cokup
cokmedigine bakar.

Neden var: duman_testi.py sadece saf fonksiyonlari (skorlama, siralama)
test ediyordu. Cizim fonksiyonlarindaki hatalar yakalanmiyordu. Coklu niyet
eklenirken karsilastirma modu iki niyet secilince TypeError ile coktu ve
hicbir test bunu gormedi. Bu dosya o boslugu kapatir.

Test edilen durumlar:
  - Niyet kapisi (secimsiz / tek niyet / cift niyet / sadece dolasmak)
  - Akis ekrani (tek ve coklu niyet)
  - Kapanis karti (tek ve coklu niyet)
  - Memnuniyet ekrani
  - Zaman Aynasi paneli (cevapli ve cevapsiz)
  - Karsilastirma modu (tek ve coklu niyet)

Kullanim:
    python arayuz_testi.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

BURASI = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(BURASI, "pusula.html")

# ── Sahte DOM ────────────────────────────────────────────────────────
# Uygulamanin dokundugu kadarini taklit eder. Amac tam bir tarayici
# olmak degil; cizim kodunun istisna firlatip firlatmadigini gormek.
DOM_TASLAK = r"""
function Eleman(secici) {
  this._secici = secici || "";
  this.innerHTML = "";
  this.onclick = null;
  this.onscroll = null;
  this.scrollTop = 0;
  this.scrollHeight = 5000;
  this.clientHeight = 600;
  this.dataset = {};
  this.style = { setProperty: function () {} };
  this._ozellikler = {};
}
Eleman.prototype.setAttribute = function (a, d) { this._ozellikler[a] = String(d); };
Eleman.prototype.getAttribute = function (a) {
  return Object.prototype.hasOwnProperty.call(this._ozellikler, a)
    ? this._ozellikler[a] : null;
};
Eleman.prototype.querySelector = function (s) { return new Eleman(s); };
Eleman.prototype.querySelectorAll = function () { return []; };

var SON_CIZIM = "";

var document = {
  documentElement: new Eleman(":root"),
  getElementById: function (id) { return new Eleman("#" + id); },
  querySelector: function (s) {
    var e = new Eleman(s);
    // ciz() sonucunu yakalayabilmek icin cihazlar kabini ozel tutuyoruz
    return e;
  },
  querySelectorAll: function () { return []; },
  addEventListener: function () {}
};

// #cihazlar kabini tekil olmali: ciz() ona yaziyor, biz onu okuyoruz.
var CIHAZLAR_KABI = new Eleman("#cihazlar");
document.getElementById = function (id) {
  if (id === "cihazlar") return CIHAZLAR_KABI;
  return new Eleman("#" + id);
};

var window = {
  matchMedia: function () { return { matches: false }; }
};
"""

# ── Test surucusu ────────────────────────────────────────────────────
SURUCU = r"""
const sonuclar = [];

function dene(ad, hazirla, beklenen) {
  try {
    hazirla();
    CIHAZLAR_KABI.innerHTML = "";
    ciz();
    const html = CIHAZLAR_KABI.innerHTML || "";
    const eksik = (beklenen || []).filter(b => html.indexOf(b) === -1);
    sonuclar.push({
      ad: ad,
      durum: eksik.length ? "ICERIK EKSIK" : "OK",
      uzunluk: html.length,
      eksik: eksik
    });
  } catch (e) {
    sonuclar.push({ ad: ad, durum: "COKTU", hata: String(e && e.message || e) });
  }
}

function sifirla() {
  durum.mod = "deneyim";
  durum.ekran = "kapi";
  durum.niyetler = [];
  durum.butce = 15;
  durum.harcanan = 0;
  durum.akis = [];
  durum.acikNeden = null;
  durum.memnuniyet = null;
}

dene("kapi / secimsiz", () => { sifirla(); },
     ["Bugün ne için buradasın?", "disabled"]);

dene("kapi / tek niyet", () => { sifirla(); durum.niyetler = ["ogrenmek"]; },
     ["aria-pressed=\"true\""]);

dene("kapi / cift niyet", () => { sifirla(); durum.niyetler = ["ogrenmek", "eglenmek"]; },
     ["data-kilitli"]);

dene("kapi / sadece dolasmak", () => { sifirla(); durum.niyetler = ["dolasmak"]; },
     ["data-kilitli"]);

dene("akis / tek niyet", () => {
  sifirla();
  durum.niyetler = ["ogrenmek"];
  durum.akis = pusulaSirala(durum.niyetler, akisUzunlugu());
  durum.ekran = "akis";
  // "halka-yuzde": zaman gostergesi renge ek olarak sayiyi da yaziyor mu?
  // Renk tek basina bilgi tasimamali (WCAG 1.4.1).
}, ["class=\"gonderi\"", "neden bu?", "halka-yuzde"]);

dene("akis / coklu niyet", () => {
  sifirla();
  durum.niyetler = ["ogrenmek", "eglenmek"];
  durum.akis = pusulaSirala(durum.niyetler, akisUzunlugu());
  durum.ekran = "akis";
}, ["class=\"gonderi\""]);

dene("kapanis / tek niyet", () => {
  sifirla();
  durum.niyetler = ["eglenmek"];
  durum.akis = pusulaSirala(durum.niyetler, akisUzunlugu());
  durum.harcanan = durum.butce;
  durum.ekran = "kapanis";
}, ["Bugünlük bu kadar", "Eğlendirici içerik"]);

dene("kapanis / coklu niyet", () => {
  sifirla();
  durum.niyetler = ["ogrenmek", "sosyallesmek"];
  durum.akis = pusulaSirala(durum.niyetler, akisUzunlugu());
  durum.harcanan = durum.butce;
  durum.ekran = "kapanis";
}, ["Öğretici içerik", "Sosyal içerik", "ve sosyalleşmek"]);

dene("kapanis / sadece dolasmak", () => {
  sifirla();
  durum.niyetler = ["dolasmak"];
  durum.akis = pusulaSirala(durum.niyetler, akisUzunlugu());
  durum.harcanan = durum.butce;
  durum.ekran = "kapanis";
}, ["Farklı kategori"]);

dene("memnuniyet", () => {
  sifirla();
  durum.niyetler = ["ogrenmek"];
  durum.akis = pusulaSirala(durum.niyetler, akisUzunlugu());
  durum.ekran = "memnuniyet";
}, ["Bu oturum sana iyi geldi mi?"]);

dene("panel / cevapsiz", () => {
  sifirla();
  durum.niyetler = ["ogrenmek"];
  durum.akis = pusulaSirala(durum.niyetler, akisUzunlugu());
  durum.ekran = "panel";
}, ["Zaman Aynası"]);

dene("panel / cevapli", () => {
  sifirla();
  durum.niyetler = ["ogrenmek", "eglenmek"];
  durum.akis = pusulaSirala(durum.niyetler, akisUzunlugu());
  durum.ekran = "panel";
  durum.memnuniyet = 3;
}, ["Senin cevabın", "İyi geldi"]);

dene("karsilastirma / tek niyet", () => {
  sifirla();
  durum.niyetler = ["ogrenmek"];
  durum.mod = "karsilastirma";
  // Klasik akista clickbait var; rozet renkli zeminin yaninda metni de
  // tasimali, yoksa bilgi tek basina renge binmis olur.
}, ["Klasik algoritma", "PUSULA · Öğrenmek", "clickbait işareti"]);

dene("karsilastirma / coklu niyet", () => {
  sifirla();
  durum.niyetler = ["ogrenmek", "eglenmek"];
  durum.mod = "karsilastirma";
}, ["Klasik algoritma", "PUSULA · Öğrenmek ve eğlenmek"]);

dene("karsilastirma / secimsiz", () => {
  sifirla();
  durum.mod = "karsilastirma";
}, ["Klasik algoritma"]);

console.log(JSON.stringify(sonuclar, null, 2));
"""


def calistir():
    node = shutil.which("node")
    if not node:
        print("HATA: node bulunamadi.")
        return 1

    with open(HTML, "r", encoding="utf-8") as f:
        html = f.read()
    js = html.split("<script>", 1)[1].rsplit("</script>", 1)[0]

    kaynak = DOM_TASLAK + "\n" + js + "\n" + SURUCU
    gecici = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                         encoding="utf-8")
    try:
        gecici.write(kaynak)
        gecici.close()
        sonuc = subprocess.run([node, gecici.name], capture_output=True,
                               text=True, encoding="utf-8")
    finally:
        os.unlink(gecici.name)

    if sonuc.returncode != 0:
        print("HATA: betik hic calismadi")
        print((sonuc.stderr or "")[-1200:])
        return 1

    sonuclar = json.loads(sonuc.stdout)
    basarisiz = [s for s in sonuclar if s["durum"] != "OK"]

    genislik = max(len(s["ad"]) for s in sonuclar)
    for s in sonuclar:
        if s["durum"] == "OK":
            print("  OK    %-*s  (%d karakter)" % (genislik, s["ad"], s["uzunluk"]))
        elif s["durum"] == "COKTU":
            print("  COKTU %-*s  %s" % (genislik, s["ad"], s["hata"]))
        else:
            print("  EKSIK %-*s  bulunamadi: %s"
                  % (genislik, s["ad"], ", ".join(s["eksik"])))

    print()
    if basarisiz:
        print("BASARISIZ: %d/%d ekran" % (len(basarisiz), len(sonuclar)))
        return 1
    print("TUM EKRANLAR GECTI (%d/%d)" % (len(sonuclar), len(sonuclar)))
    return 0


if __name__ == "__main__":
    sys.exit(calistir())
