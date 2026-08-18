# -*- coding: utf-8 -*-
"""
PUSULA - Duman Testi (smoke test)
=================================

Uretilen pusula.html icindeki siralama motorunu Node'da calistirir ve
gercekten gonderi dondurdugunu dogrular.

Neden var: "syntax OK" sayfanin calistigini kanitlamaz. Bir kere JS'in
tamami sessizce dusmus, ekran bombos acilmis, kimse fark etmemisti. Bu
test akisin dolu geldigini ve Python tarafiyla ayni sonucu verdigini
gosterir.

Kullanim:
    python duman_testi.py
"""

import os
import shutil
import subprocess
import sys
import tempfile

BURASI = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(BURASI, "pusula.html")

# Sayfanin JS'inden alacagimiz bolum: veri + saf skorlama fonksiyonlari.
# "/* ── Durum ─" isaretinden sonrasi DOM'a dokunuyor, Node'da calismaz.
KESME_ISARETI = "/* ── Durum ─"

SURUCU = """
const NIYET_ADLARI = Object.keys(NIYETLER);
const cikti = { havuz: HAVUZ.length, niyetler: {} };

for (const ad of NIYET_ADLARI) {
  const akis = pusulaSirala([ad]);
  const m = metrikler(akis, [ad]);
  cikti.niyetler[ad] = {
    adet: akis.length,
    uyum: +m.uyum.toFixed(3),
    tatmin: +m.tatmin.toFixed(3),
    pismanlik: +m.pismanlik.toFixed(3),
    clickbait: +m.clickbait.toFixed(3),
    ilk: akis[0] ? akis[0].m.slice(0, 50) : null
  };
}

// Coklu niyet: her ikili kombinasyon denenir. Beklenti, birlesik akisin
// her iki niyeti de tek tek secilmis halinden cok daha kotu olmamasi ve
// her iki niyetin hedef kategorilerinden de gonderi icermesi.
const HEDEF = {
  ogrenmek:       ["egitim_anlatim", "nasil_yapilir", "bilim_teknoloji"],
  eglenmek:       ["mizah", "eglence_video"],
  haberdar_olmak: ["son_dakika_haber", "gundem_analiz"],
  sosyallesmek:   ["arkadas_paylasimi", "soru_tartisma"]
};
const COKLU = Object.keys(HEDEF);
cikti.ikili = {};
for (let i = 0; i < COKLU.length; i++) {
  for (let j = i + 1; j < COKLU.length; j++) {
    const cift = [COKLU[i], COKLU[j]];
    const akis = pusulaSirala(cift);
    const m = metrikler(akis, cift);
    const ilk20 = akis.slice(0, 20);
    cikti.ikili[cift.join("+")] = {
      adet: akis.length,
      uyum: +m.uyum.toFixed(3),
      clickbait: +m.clickbait.toFixed(3),
      // Ilk 20'de her iki niyetin hedef kategorilerinden kac gonderi var
      birinci: ilk20.filter(g => HEDEF[cift[0]].includes(g.k)).length,
      ikinci:  ilk20.filter(g => HEDEF[cift[1]].includes(g.k)).length
    };
  }
}

const kl = klasikSirala();
const mk = metrikler(kl, ["ogrenmek"]);
cikti.klasik = {
  adet: kl.length,
  uyum: +mk.uyum.toFixed(3),
  clickbait: +mk.clickbait.toFixed(3)
};

// Butce dolabiliyor mu? Akis, secilen butceyi tuketecek kadar uzun olmali;
// yoksa kapanis ekranina hic ulasilamaz.
cikti.butceler = {};
for (const butce of [15, 30, 40]) {
  const istenen = Math.min(50, Math.round(butce * 2));
  const akis = pusulaSirala(["ogrenmek"], istenen);
  cikti.butceler[butce] = { istenen, gelen: akis.length };
}

console.log(JSON.stringify(cikti, null, 2));
"""


def js_cikar():
    with open(HTML, "r", encoding="utf-8") as f:
        html = f.read()
    js = html.split("<script>", 1)[1].rsplit("</script>", 1)[0]
    if KESME_ISARETI not in js:
        raise RuntimeError("Kesme isareti bulunamadi; sablon degismis olabilir.")
    return js.split(KESME_ISARETI, 1)[0]


def calistir():
    node = shutil.which("node")
    if not node:
        print("HATA: node bulunamadi, test calistirilamiyor.")
        return 1

    kaynak = js_cikar() + SURUCU
    gecici = tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False,
                                         encoding="utf-8")
    try:
        gecici.write(kaynak)
        gecici.close()
        sonuc = subprocess.run([node, gecici.name], capture_output=True,
                               text=True, encoding="utf-8")
    finally:
        os.unlink(gecici.name)

    if sonuc.returncode != 0:
        print("HATA: motor calismadi")
        print((sonuc.stderr or "")[-800:])
        return 1

    print(sonuc.stdout)

    # Kabul kriterleri
    import json
    d = json.loads(sonuc.stdout)
    hatalar = []
    if d["havuz"] < 100:
        hatalar.append("Havuz cok kucuk: %d" % d["havuz"])
    for ad, s in d["niyetler"].items():
        if s["adet"] == 0:
            hatalar.append("%s: akis BOS" % ad)
        if s["clickbait"] > 0:
            hatalar.append("%s: akista clickbait var (%.2f)" % (ad, s["clickbait"]))
        if s["uyum"] < 0.6:
            hatalar.append("%s: niyet uyumu dusuk (%.2f)" % (ad, s["uyum"]))

    # Coklu niyet: akis her iki niyete de hizmet etmeli. Tek bir niyetin
    # digerini tamamen ezmesi, cok secimli kapiyi anlamsiz kilar.
    for cift, s in d["ikili"].items():
        if s["clickbait"] > 0:
            hatalar.append("%s: akista clickbait var (%.2f)" % (cift, s["clickbait"]))
        if s["uyum"] < 0.6:
            hatalar.append("%s: niyet uyumu dusuk (%.2f)" % (cift, s["uyum"]))
        if s["birinci"] == 0 or s["ikinci"] == 0:
            hatalar.append("%s: ilk 20'de bir niyet hic temsil edilmiyor (%d/%d)"
                           % (cift, s["birinci"], s["ikinci"]))

    for butce, b in d["butceler"].items():
        if b["gelen"] < b["istenen"]:
            hatalar.append("%s dk butce: akis kisa kaliyor (%d/%d) - "
                           "kapanis ekranina ulasilamaz"
                           % (butce, b["gelen"], b["istenen"]))

    if hatalar:
        print("BASARISIZ:")
        for h in hatalar:
            print("  - " + h)
        return 1

    print("TUM KONTROLLER GECTI")
    print("  Akis dolu, clickbait sizmiyor, niyet uyumu esigin ustunde.")
    return 0


if __name__ == "__main__":
    sys.exit(calistir())
