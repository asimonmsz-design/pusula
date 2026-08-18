# -*- coding: utf-8 -*-
"""
PUSULA - Erisilebilirlik Denetimi
=================================

Raporda erisilebilirlik hakkinda iddia edilen her seyi otomatik olarak
sinar. Amac su cumleyi dogru kilmaktir: "erisilebilirlik bir niyet beyani
olarak degil, olculen ve test edilen bir sart olarak ele alinmistir."

Neden var: kontrast_olc.py yalnizca RENKLERI olcuyordu. Belgenin kendisine
- dil etiketi, karakter kodlamasi, baslik sirasi, ARIA gecerliligi, klavye
erisimi - hicbir test bakmiyordu. Bu boslugun somut bir bedeli oldu:
sablon.html uzun sure <!doctype>, <meta charset> ve lang="tr" olmadan
kaldi. Tarayici kodlamayi tahmin ettigi icin hata yerel makinede
gorunmuyordu; baska bir ortamda sayfa bozuk karakterlerle aciliyordu.
Rapor ise lang="tr" oldugunu yaziyordu. Bu dosya o sinif hatalari yakalar.

Denetim iki katmanda calisir:
  1) Duragan katman - pusula.html'in kendisi: belge iskeleti ve CSS.
  2) Uretilen katman - arayuz_testi.py'deki sahte DOM ile butun ekranlar
     cizdirilir ve JavaScript'in URETTIGI isaret dili denetlenir. Kaynak
     dosyada arama yapmak yeterli degildir; kullanicinin gordugu isaret
     dilini uc anda JavaScript uretir.

Kullanim:
    python erisilebilirlik_testi.py

Cikis kodu: hata varsa 1, temizse 0.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BURASI = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(BURASI, "pusula.html")

# ── Sonuc toplama ────────────────────────────────────────────────────
SONUC = []


def denetle(bolum, ad, gecti, kanit=""):
    SONUC.append({"bolum": bolum, "ad": ad, "gecti": bool(gecti), "kanit": kanit})


def kisalt(metin, n=58):
    metin = " ".join(str(metin).split())
    return metin if len(metin) <= n else metin[: n - 1] + "…"


# ── Gecerli ARIA sozlugu (WAI-ARIA 1.2, kullandigimiz altkume) ───────
GECERLI_ROL = {
    "alert", "banner", "button", "checkbox", "complementary", "contentinfo",
    "dialog", "document", "feed", "form", "group", "heading", "img", "link",
    "list", "listitem", "main", "navigation", "none", "note", "presentation",
    "progressbar", "radio", "radiogroup", "region", "row", "search", "status",
    "switch", "tab", "table", "tablist", "tabpanel", "toolbar", "tooltip",
}

GECERLI_ARIA = {
    "aria-atomic", "aria-busy", "aria-checked", "aria-controls", "aria-current",
    "aria-describedby", "aria-disabled", "aria-expanded", "aria-hidden",
    "aria-label", "aria-labelledby", "aria-live", "aria-modal", "aria-pressed",
    "aria-relevant", "aria-required", "aria-selected", "aria-valuemax",
    "aria-valuemin", "aria-valuenow", "aria-valuetext",
}

# aria-pressed yalnizca dugmede anlamlidir; aria-selected sekme/secenekte.
ARIA_YERI = {
    "aria-pressed": ("button",),
    "aria-selected": ("tab", "option", "row"),
}


# ── 1. Duragan katman: belge iskeleti ────────────────────────────────
def iskelet_denetle(ham):
    bas = ham[:1500]

    denetle("Belge iskeleti", "<!doctype html> bildirimi",
            re.match(r"\s*<!doctype html>", ham, re.I) is not None,
            "yoksa tarayici 'quirks mode'a duser")

    m = re.search(r"<html\b[^>]*\blang\s*=\s*[\"']([^\"']+)[\"']", bas, re.I)
    denetle("Belge iskeleti", 'html lang="tr" dil etiketi',
            m is not None and m.group(1).lower().startswith("tr"),
            'lang="%s"' % m.group(1) if m else "lang yok — ekran okuyucu "
            "Turkce metni Ingilizce telaffuz eder")

    m = re.search(r"<meta\b[^>]*\bcharset\s*=\s*[\"']?([\w-]+)", bas, re.I)
    denetle("Belge iskeleti", "meta charset=utf-8",
            m is not None and m.group(1).lower() in ("utf-8", "utf8"),
            "charset=%s" % m.group(1) if m else "yoksa Turkce harfler bozulur")

    denetle("Belge iskeleti", "meta viewport (mobil olcek)",
            re.search(r"<meta\b[^>]*name\s*=\s*[\"']viewport[\"']", bas, re.I)
            is not None, "dar ekranda yakinlastirma dogru calissin")

    m = re.search(r"<title>(.*?)</title>", ham, re.S | re.I)
    denetle("Belge iskeleti", "<title> dolu",
            m is not None and len(m.group(1).strip()) > 3,
            kisalt(m.group(1)) if m else "baslik yok")

    denetle("Belge iskeleti", "head ve body kapatilmis",
            "</head>" in ham.lower() and "</body>" in ham.lower(),
            "belge agaci acikta kalmasin")


# ── 2. Duragan katman: CSS'te yer alan erisilebilirlik onlemleri ─────
def css_denetle(ham):
    stil = "".join(re.findall(r"<style>(.*?)</style>", ham, re.S | re.I))

    denetle("Uslup (CSS)", ":focus-visible odak cercevesi tanimli",
            ":focus-visible" in stil,
            "klavyeyle gezen kullanici nerede oldugunu gorsun")

    denetle("Uslup (CSS)", "prefers-reduced-motion destegi",
            "prefers-reduced-motion" in stil,
            "hareket duyarliligi olan kullanici icin animasyon kapanir")

    # Gorsel olarak gizli metin display:none ile gizlenirse ekran okuyucu da
    # okumaz. Dogru yontem clip/clip-path ile gorsel alandan cikarmaktir.
    m = re.search(r"\.sr-only\s*\{(.*?)\}", stil, re.S)
    icerik = m.group(1) if m else ""
    denetle("Uslup (CSS)", "sr-only ekran okuyucudan gizlenmiyor",
            m is not None and "display:none" not in icerik.replace(" ", "")
            and ("clip" in icerik),
            kisalt(icerik.replace("\n", " ")) if m else "sr-only sinifi yok")

    denetle("Uslup (CSS)", "telefon cercevesi dar ekranda esniyor",
            "min(" in stil, "sabit genislik dar ekranda tasma yapar")


# ── 3. Uretilen katman: butun ekranlarin isaret dilini cizdir ────────
def ekranlari_ciz():
    """arayuz_testi.py'deki sahte DOM ile her ekranin HTML'ini uretir."""
    node = shutil.which("node")
    if not node:
        return None

    sys.path.insert(0, BURASI)
    import arayuz_testi as at  # sahte DOM tanimini tekrar yazmiyoruz

    with open(HTML, "r", encoding="utf-8") as f:
        html = f.read()
    js = html.split("<script>", 1)[1].rsplit("</script>", 1)[0]

    surucu = r"""
const cikti = {};
function sifirla() {
  durum.mod = "deneyim"; durum.ekran = "kapi"; durum.niyetler = [];
  durum.butce = 15; durum.harcanan = 0; durum.akis = [];
  durum.acikNeden = null; durum.memnuniyet = null;
}
function yakala(ad, hazirla) {
  sifirla(); hazirla();
  CIHAZLAR_KABI.innerHTML = ""; ciz();
  cikti[ad] = CIHAZLAR_KABI.innerHTML || "";
}
yakala("niyet kapisi", () => {});
yakala("niyet kapisi / secili", () => { durum.niyetler = ["ogrenmek"]; });
yakala("akis", () => {
  durum.niyetler = ["ogrenmek"];
  durum.akis = pusulaSirala(durum.niyetler, akisUzunlugu());
  durum.ekran = "akis";
});
yakala("akis / neden bu acik", () => {
  durum.niyetler = ["ogrenmek"];
  durum.akis = pusulaSirala(durum.niyetler, akisUzunlugu());
  durum.ekran = "akis"; durum.acikNeden = 0;
});
yakala("kapanis karti", () => {
  durum.niyetler = ["ogrenmek"];
  durum.akis = pusulaSirala(durum.niyetler, akisUzunlugu());
  durum.ekran = "kapanis"; durum.harcanan = durum.butce;
});
yakala("memnuniyet", () => {
  durum.niyetler = ["ogrenmek"];
  durum.akis = pusulaSirala(durum.niyetler, akisUzunlugu());
  durum.ekran = "memnuniyet";
});
yakala("karsilastirma", () => {
  durum.mod = "karsilastirma"; durum.niyetler = ["ogrenmek"];
});
console.log(JSON.stringify(cikti));
"""

    gecici = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                         encoding="utf-8")
    try:
        gecici.write(at.DOM_TASLAK + "\n" + js + "\n" + surucu)
        gecici.close()
        sonuc = subprocess.run([node, gecici.name], capture_output=True,
                               text=True, encoding="utf-8")
        if sonuc.returncode != 0:
            raise RuntimeError("Ekranlar cizilemedi:\n" + (sonuc.stderr or ""))
        return json.loads(sonuc.stdout.strip().splitlines()[-1])
    finally:
        os.unlink(gecici.name)


# ── 4. Uretilen isaret dilinin denetimi ──────────────────────────────
ETIKET = re.compile(r"<(\w+)((?:\s+[-\w:]+(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+))?)*)\s*/?>")
OZNITELIK = re.compile(r"([-\w:]+)(?:\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+)))?")


def etiketleri_coz(html):
    """(etiket_adi, {oznitelik: deger}, ham_metin) uretir."""
    for m in ETIKET.finditer(html):
        ad = m.group(1).lower()
        oz = {}
        for o in OZNITELIK.finditer(m.group(2) or ""):
            deger = o.group(2)
            if deger is None:
                deger = o.group(3)
            if deger is None:
                deger = o.group(4)
            oz[o.group(1).lower()] = deger if deger is not None else ""
        yield ad, oz, m.group(0)


def isaret_dili_denetle(parcalar):
    """parcalar: {ekran_adi: html}. Duragan iskelet de bir parcadir."""
    rol_hatasi, aria_hatasi, yer_hatasi = [], [], []
    tabindex_hatasi, adsiz_dugme, altsiz_gorsel = [], [], []
    tiklanabilir_div = []
    basliklar = []
    canli_bolge = False

    for ekran, html in parcalar.items():
        for ad, oz, ham in etiketleri_coz(html):
            rol = oz.get("role", "")
            if rol and rol not in GECERLI_ROL:
                rol_hatasi.append("%s: role=\"%s\"" % (ekran, rol))
            if rol in ("status", "alert") or oz.get("aria-live"):
                canli_bolge = True

            for anahtar in oz:
                if anahtar.startswith("aria-") and anahtar not in GECERLI_ARIA:
                    aria_hatasi.append("%s: %s" % (ekran, anahtar))
                if anahtar in ARIA_YERI:
                    uygun = ARIA_YERI[anahtar]
                    yerinde = (ad in uygun) or (rol in uygun)
                    if not yerinde:
                        yer_hatasi.append("%s: <%s> uzerinde %s"
                                          % (ekran, ad, anahtar))

            ti = oz.get("tabindex")
            if ti and ti.strip().lstrip("+").isdigit() and int(ti) > 0:
                tabindex_hatasi.append("%s: tabindex=%s" % (ekran, ti))

            if ad == "img" and "alt" not in oz:
                altsiz_gorsel.append("%s: %s" % (ekran, kisalt(ham, 40)))

            if ad in ("div", "span") and ("onclick" in oz or "data-tikla" in oz):
                tiklanabilir_div.append("%s: %s" % (ekran, kisalt(ham, 40)))

            if re.fullmatch(r"h[1-6]", ad):
                basliklar.append((ekran, int(ad[1])))

        # Dugmelerin erisilebilir adi: ya ic metin ya aria-label
        for m in re.finditer(r"<button\b([^>]*)>(.*?)</button>", html, re.S):
            oz_ham, ic = m.group(1), m.group(2)
            metin = re.sub(r"<[^>]+>", " ", ic).strip()
            if not metin and "aria-label" not in oz_ham.lower():
                adsiz_dugme.append("%s: %s" % (ekran, kisalt(m.group(0), 40)))

    # Baslik sirasi: bir duzey atlanmamali (h1 -> h3 olmaz)
    atlama = []
    for ekran in parcalar:
        sira = [d for e, d in basliklar if e == ekran]
        for onceki, simdiki in zip(sira, sira[1:]):
            if simdiki - onceki > 1:
                atlama.append("%s: h%d -> h%d" % (ekran, onceki, simdiki))

    denetle("Isaret dili", "role degerleri gecerli",
            not rol_hatasi, "; ".join(rol_hatasi[:3]) or "tumu WAI-ARIA sozlugunde")
    denetle("Isaret dili", "aria-* oznitelik adlari gecerli",
            not aria_hatasi, "; ".join(aria_hatasi[:3]) or "yazim hatasi yok")
    denetle("Isaret dili", "aria-pressed / aria-selected dogru ogede",
            not yer_hatasi, "; ".join(yer_hatasi[:3]) or "durum bildirimleri yerinde")
    denetle("Isaret dili", "pozitif tabindex yok",
            not tabindex_hatasi, "; ".join(tabindex_hatasi[:3])
            or "klavye sirasi belge sirasini izler")
    denetle("Isaret dili", "her dugmenin erisilebilir adi var",
            not adsiz_dugme, "; ".join(adsiz_dugme[:3]) or "bos dugme yok")
    denetle("Isaret dili", "gorsellerde alt metni var",
            not altsiz_gorsel, "; ".join(altsiz_gorsel[:3]) or "alt'siz <img> yok")
    denetle("Isaret dili", "tiklanabilir ogeler semantik (div degil)",
            not tiklanabilir_div, "; ".join(tiklanabilir_div[:3])
            or "tiklanan her oge <button> veya <a>")
    denetle("Isaret dili", "baslik duzeyi atlanmiyor",
            not atlama, "; ".join(atlama[:3]) or "h1 -> h2 -> h3 sirasi korunuyor")
    denetle("Isaret dili", "canli bolge (role=status) var",
            canli_bolge, "akis yeniden siralandiginda tek cumleyle duyurulur")


# ── 5. Renk tek basina bilgi tasimasin (WCAG 1.4.1) ──────────────────
def renk_bagimsizligi_denetle(ekranlar):
    akis = ekranlar.get("akis", "")
    karsilastirma = ekranlar.get("karsilastirma", "")
    kapanis = ekranlar.get("kapanis karti", "")

    denetle("Renk bagimsizligi", "zaman halkasinin yaninda yuzde yazili",
            "halka-yuzde" in akis or "halka-yuzde" in kapanis,
            "renk gorulmese de kalan sure okunur")
    denetle("Renk bagimsizligi", "clickbait rozeti metin iceriyor",
            "clickbait i" in karsilastirma.lower(),
            "kirmizi zemin tek basina bilgi tasimiyor")
    denetle("Renk bagimsizligi", "secili niyet aria-pressed ile isaretli",
            'aria-pressed="true"' in ekranlar.get("niyet kapisi / secili", ""),
            "secim rengi gormeyene de bildirilir")


# ── 6. Rapor ─────────────────────────────────────────────────────────
def bas():
    print()
    print("PUSULA - ERISILEBILIRLIK DENETIMI")
    print("=" * 72)

    bolum = None
    for s in SONUC:
        if s["bolum"] != bolum:
            bolum = s["bolum"]
            print()
            print(bolum.upper())
            print("-" * 72)
        isaret = "OK  " if s["gecti"] else "HATA"
        print("  %s  %-44s %s" % (isaret, s["ad"], kisalt(s["kanit"])))

    gecen = sum(1 for s in SONUC if s["gecti"])
    print()
    print("=" * 72)
    if gecen == len(SONUC):
        print("TUM DENETIMLER GECTI (%d/%d)" % (gecen, len(SONUC)))
        return 0
    print("DENETIM BASARISIZ (%d/%d gecti)" % (gecen, len(SONUC)))
    for s in SONUC:
        if not s["gecti"]:
            print("  - %s: %s" % (s["ad"], s["kanit"]))
    return 1


def main():
    with open(HTML, "r", encoding="utf-8") as f:
        ham = f.read()

    iskelet_denetle(ham)
    css_denetle(ham)

    # Duragan iskelet (header, sekmeler, tema dugmesi) da denetlenmeli.
    duragan = ham.split("<script>", 1)[0]
    parcalar = {"duragan iskelet": duragan}

    ekranlar = ekranlari_ciz()
    if ekranlar is None:
        print("UYARI: node bulunamadi, uretilen ekranlar denetlenemedi.")
        ekranlar = {}
    parcalar.update(ekranlar)

    isaret_dili_denetle(parcalar)
    if ekranlar:
        renk_bagimsizligi_denetle(ekranlar)

    print("Denetlenen ekran sayisi: %d (duragan iskelet dahil)" % len(parcalar))
    return bas()


if __name__ == "__main__":
    sys.exit(main())
