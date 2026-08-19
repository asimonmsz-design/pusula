# PUSULA

### Niyet odaklı akış ve dijital refah sistemi

Sosyal medya akışını, kullanıcının ekranda geçirdiği **süreye** göre değil, oturuma
başlarken **beyan ettiği niyete** göre sıralayan bir arayüz ve öneri sistemi.

> **TEKNOFEST NSosyal İnovasyon Yarışması 2026**
> Tema: Kullanıcı Katılımı ve Arayüz (UI/UX)

### 🧭 [Çalışan prototipi tarayıcıda aç](https://asimonmsz-design.github.io/pusula/)

Kurulum, hesap veya klonlama gerekmez. "Karşılaştırma" sekmesi klasik sıralamayla
PUSULA sıralamasını yan yana gösterir.

---

## Problem

Bugünkü sıralama algoritmaları tek bir soruyu optimize eder: *kullanıcı ekranda ne kadar
kalır?* Bu soru, kullanıcının **ne için geldiğini** hiç sormaz. Sonuç, herkesin tanıdığı
tablodur — bir şey öğrenmek için açılan uygulamadan kırk dakika sonra hiçbir şey
öğrenmeden çıkmak.

Ölçtüğümüz kadarıyla sorun niyete göre değişiyor: klasik akış **eğlenme** ve **dolaşma**
niyetine makul biçimde hizmet ediyor (uyum 0.55), ama **sosyalleşme** (0.19) ve
**öğrenme** (0.26) niyetlerinde neredeyse tamamen başarısız oluyor.

## Çözüm

Kullanıcı girişte tek dokunuşla niyetini belirtir — *öğrenmek · eğlenmek · haberdar olmak ·
sosyalleşmek · sadece dolaşmak*. Sistem akışı bu hedefe göre yeniden kurar. Oturum
sonundaki memnuniyet geri bildirimi sıralama modelinin ödül sinyali olur.

**Sıralama formülü — fark tam olarak burada:**

```
Klasik :  skor = 0.70 × etkileşim + 0.20 × tazelik + 0.10 × spam_filtresi

PUSULA :  taban = 0.70 × niyet_uyumu + 0.15 × tazelik + 0.15 × etkileşim
          skor  = taban × kalite          ← çarpımsal kapı, toplamsal terim değil
```

Kalitenin **çarpımsal** olması kritik: toplamsal terim olarak denendiğinde clickbait
içerik yüksek etkileşimiyle cezayı telafi edip akışta %25 oranında hayatta kalıyordu.
Çarpımsal kapıya çevrildiğinde bu oran %0'a indi.

---

## Hızlı başlangıç

Python 3 dışında **hiçbir bağımlılık yok.** İnternet, API anahtarı veya kurulum gerekmez.

```bash
# 1. 2000 sentetik Türkçe gönderiden oluşan içerik havuzunu üret
python kod/icerik_uret.py

# 2. Gönderileri niyet vektörleriyle etiketle
python kod/niyet_etiketle.py

# 3. Beş niyet için klasik vs PUSULA karşılaştırma tablosunu al
python kod/deney_sonuclari.py

# 4. Tek dosyalık web prototipini üret -> tasarim/pusula.html
python tasarim/uygulama_uret.py
```

Dördüncü adımdan sonra `tasarim/pusula.html` dosyasını tarayıcıda açmanız yeterli.
Kurmadan denemek isterseniz: **https://asimonmsz-design.github.io/pusula/**

**Tekrarlanabilirlik:** üretim rastgele tohumla sabitlenmiştir (`random.seed(42)`), zincir
baştan sona yeniden çalıştırıldığında bu depodaki bütün sayılar **birebir** yeniden üretilir.
Aşağıdaki tablolardaki hiçbir değer elle yazılmamıştır; hepsi `kod/veri/deney_sonuclari.txt`
dosyasından gelir.

### Testler

```bash
python tasarim/duman_testi.py            # sıralama motoru Node'da uçtan uca doğrulanır
python tasarim/arayuz_testi.py           # 15 ekranın tamamı render edilir
python tasarim/kontrast_olc.py           # WCAG 2.1 AA kontrast denetimi
python tasarim/erisilebilirlik_testi.py  # belge iskeleti, ARIA, klavye, başlık sırası
python kod/kontrol_clickbait.py          # clickbait tespit doğruluğu
```

---

## Klasör yapısı

```
PUSULA/
├── kod/                          Sıralama motoru ve deneyler
│   ├── icerik_uret.py            2000 sentetik Türkçe gönderi üretir
│   ├── niyet_etiketle.py         Gönderilerin niyet vektörünü tahmin eder
│   ├── siralama.py               Sıralama motoru (klasik + PUSULA)
│   ├── deney_sonuclari.py        Beş niyet için ölçüm tablosu
│   ├── kontrol_clickbait.py      Clickbait tespit doğruluğu kontrolü
│   ├── demo.py                   Terminalde yan yana karşılaştırma
│   └── veri/                     Üretilen veri ve ölçüm çıktıları
│
├── tasarim/                      Arayüz ve erişilebilirlik
│   ├── sablon.html               Uygulama şablonu (veri yer tutuculu)
│   ├── uygulama_uret.py          Şablon + veri -> pusula.html
│   ├── pusula.html               Çalışan tek dosyalık prototip (üretilir)
│   ├── arayuz_testi.py           15 ekranın render testi
│   ├── duman_testi.py            Motorun Node'da uçtan uca doğrulanması
│   ├── kontrast_olc.py           WCAG 2.1 AA kontrast ölçümü
│   ├── erisilebilirlik_testi.py  Belge iskeleti, ARIA ve klavye denetimi (22 kontrol)
│   ├── ekran/                    Prototipten alınan ekran görüntüleri (rapordaki şekiller)
│   └── qr_uret.py                Anket için QR kod ve afiş üreteci
│
└── index.html                    GitHub Pages giriş sayfası
```

Modelin ayrıntıları, kullanıcı akışları, erişilebilirlik denetimi, veri ve etik
değerlendirmesi ile kullanıcı araştırmasının yöntemi teknik raporda açıklanmıştır.
Rapor yarışmaya ayrıca teslim edildiği için bu depoda paylaşılmamaktadır.

---

## Kişisel veri ve gizlilik

Bu depo **hiçbir kişisel veri içermez.** Tüm içerik sentetik olarak üretilmiştir; gerçek
kullanıcı gönderisi, hesap adı veya davranış kaydı kullanılmamıştır. Yarışma değerlendirme
esasları gereği takım üyelerinin isim ve fotoğraf bilgileri ne raporda ne bu depoda yer alır.

Kullanıcı araştırması anketi anonimdir, e-posta toplamaz ve kimlik bilgisi içermez;
ankete ilişkin yöntem, örneklem sınırları ve önceden kaydedilmiş beklentiler teknik
raporda açıklanmıştır. Ham yanıtlar bu depoda paylaşılmamaktadır.

---

## Mevcut sonuçlar

**Niyet etiketleme isabeti**

| Metrik | Değer |
|---|---|
| Baskın niyet isabeti | %96.5 |
| Ortalama mutlak hata | 0.200 |
| Clickbait yakalama (recall) | %100 |
| Clickbait yanlış alarm | %0 |

**Akış karşılaştırması** (5 niyet ortalaması, ilk 20 gönderi)

| Metrik | Klasik | PUSULA | Değişim |
|---|---|---|---|
| Niyet uyumu | 0.398 | 0.800 | **+101%** |
| Beklenen tatmin | 0.243 | 0.663 | **+173%** |
| Pişmanlık olasılığı | 0.390 | 0.173 | **−56%** |
| Clickbait oranı | %25 | %0 | **−100%** |
| Etkileşim puanı | 0.866 | 0.583 | −33% |

---

## Önemli metodolojik notlar

Bu notlar teknik raporda da açıkça yer alır. Sonuçların nasıl okunması gerektiğini belirlerler.

1. **Veri sentetiktir.** Gerçek platform verisine erişimimiz yok ve gerçek kullanıcı verisi kullanmak KVKK izni gerektirirdi. Sentetik veri, her gönderinin gerçek niyet vektörünü bilmemizi sağlar — bu da etiketleyicinin isabetini ölçmemize imkân verir.

2. **%96.5 isabet iyimser bir sayıdır.** Metinler şablonlardan üretildiği için düzenlidir. Gerçek kullanıcı metninde (argo, ironi, yazım hatası) bu oran belirgin şekilde düşer. Ürün sürümünde sezgisel etiketleyici değil, Türkçe dil modeli kullanılır; sezgisel mod yedek katmandır.

3. **Baseline kasten güçlü tutulmuştur.** İlk denemede klasik algoritmayı "sadece etkileşim" olarak modelledik ve akışın ilk 10'unun %100'ü clickbait çıktı — bu, gerçek platformları haksız şekilde kötü gösteren bir kurgudur. Klasik algoritmaya da temel spam filtresi ve çeşitlilik kısıtı verdik. PUSULA'nın üstünlüğü artık makul bir rakibe karşı ölçülüyor.

4. **Anlamlı olan mutlak değerler değil, yönsel farktır.** Gerçek veriyle sayılar değişir; iki algoritma arasındaki fark yönü korunması beklenen bulgudur.

5. **Etkileşim puanındaki düşüş beklenen bir sonuçtur**, kusur değil. Düşen kısım ağırlıklı olarak clickbait ve amaçsız kaydırma kaynaklı etkileşimdir. PUSULA formülünde etkileşim %15 ağırlıkla korunur; amaç onu yok etmek değil, tek hakem olmaktan çıkarmaktır.

---

## Geliştirme sırasında bulunan hatalar

Projenin doğrulama süreci bu tabloda kayıtlıdır: her hata nasıl bulundu ve nasıl çözüldü.

| # | Hata | Nasıl bulundu | Çözüm |
|---|---|---|---|
| 1 | Etiketleyici isabeti %84.7'de takılı; `gundem_analiz` %0 | Kategori bazlı isabet tablosu | Anahtar kelime ağırlıkları düzeltildi → %96.6 |
| 2 | Clickbait sinyali niyet vektörünü bozuyordu | Mimari gözden geçirme | Clickbait ayrı bir sinyal olarak ayrıldı |
| 3 | Klasik baseline kasten zayıftı | Kendi kendine denetim | Baseline'a spam filtresi + çeşitlilik kısıtı verildi |
| 4 | Clickbait PUSULA akışında %25 hayatta kalıyordu | Deney tablosunun CB sütunu | Kalite toplamsal terimden çarpımsal kapıya çevrildi → %0 |
| 5 | Python `"İ".lower()` iki karakter döndürüyor, eşleşme bozuluyordu | İsabet %96.6'dan %92.7'ye düştü | Türkçe'ye özel dönüşüm eklendi → %96.5 |
| 6 | **Web uygulaması bomboş açılıyordu** | Kullanıcı ekran görüntüsü | Aşağıda |
| 7 | **Zaman bütçesi hiç dolmuyordu**, halka ~%77'de takılıyordu | Kullanıcı denemesi | Tüketim akış ilerlemesine bağlandı |
| 8 | Kapanış özeti niyetten bağımsız hep "Öğretici içerik" yazıyordu | Kullanıcı denemesi | Özet satırı niyete göre değişiyor |
| 9 | "Gördüğün gönderi" olarak dakika sayısı yazılıyordu | 8'i düzeltirken | Gönderi sayısı ilerlemeden türetiliyor |
| 10 | Zaman Aynası'nda uydurma veri ("bu haftanın özeti") | 8'i düzeltirken | Tek oturum olduğu açıkça yazılıyor |
| 11 | "Cevabın akışı eğiten tek sinyal" deniyordu, cevap hiçbir yere gitmiyordu | Kendi kendine denetim | Cevap saklanıyor ve özette gösteriliyor; ürün vaadi ayrıştırıldı |
| 12 | Karşılaştırma modu iki niyet seçilince TypeError ile çöküyordu | Çoklu niyet sonrası denetim | Etiket fonksiyonu diziyi kabul ediyor |
| 13 | Beş renk çifti WCAG AA eşiğinin altındaydı | `kontrast_olc.py` (yeni) | Renk jetonları düzeltildi |
| 14 | Sayfa dili tanımsızdı (`lang`) | Erişilebilirlik denetimi | `document.documentElement.lang = "tr"` |
| 15 | Akış değişimi ekran okuyucuya bildirilmiyordu | Erişilebilirlik denetimi | `role="status"` canlı bölge eklendi |
| 16 | Telefon çerçevesi sabit 336×668'di, dar ekranda taşıyordu | Erişilebilirlik denetimi | `min()` ile esnetildi |

**6 numaralı hata neden önemli:** Şablondaki yer tutucu `/*__VERI__*/[]` biçimindeydi, üretici ise sadece `/*__VERI__*/` kısmını değiştiriyordu. Geriye `const HAVUZ = [...450 gönderi...][];` kalıyordu — geçersiz JavaScript. Tek bir syntax hatası `<script>` bloğunun tamamını düşürdüğü için sayfa **hiçbir hata göstermeden** boş açılıyordu.

Ders: sessiz başarısızlık, gürültülü başarısızlıktan tehlikelidir. Artık iki koruma var:

- `uygulama_uret.py` üretimden sonra JS'i `node --check` ile doğrular, geçersizse üretim başarısız olur.
- `duman_testi.py` sıralama motorunu Node'da çalıştırır; akışın dolu geldiğini, clickbait sızmadığını ve niyet uyumunun eşiğin üstünde olduğunu kontrol eder.

**7 numaralı hata neden önemli:** Zaman bütçesi tüketimi sabit piksel oranına bağlıydı — her 118 piksel bir gönderi sayılıyordu. Akış ise bütçeden bağımsız olarak hep 40 gönderiydi. 15 dakikalık bütçe zar zor doluyordu; 30 dakikalık bütçe **hiç dolmuyordu**. Kullanıcı sonuna kadar kaydırıyor, halka %77'de takılıyor, kapanış ekranı hiç gelmiyordu.

Bu, 6 numaralı hatadan daha kötüydü: uygulama çalışıyor *görünüyordu*. Ama ulaşılamayan ekran, projenin **tezinin ta kendisiydi** — "akış kesilmedi, tamamlandı" kartı. Sonsuz kaydırmaya alternatif iddia eden bir prototipte, doğal bitişin denenememesi demoyu anlamsız kılardı.

Çözüm: tüketim artık akıştaki ilerlemeye bağlı (sonuna gelmek bütçeyi tam bitirir), akış uzunluğu bütçeyle orantılı (gönderi başına ~30 sn), ve tüketim geri sarmıyor — yukarı kaydırmak harcanan zamanı geri getirmiyor. `duman_testi.py` artık her bütçe seçeneği için akışın yeterince uzun olduğunu da kontrol ediyor.

**8–10 numaralı hatalar neden önemli:** Kapanış kartı, niyet ne olursa olsun "Öğretici içerik: N" yazıyordu. Eğlenmek için gelen kullanıcıya öğretici içerik sayısı göstermek, niyet odaklı olduğunu iddia eden bir sistemde **iddianın kendisiyle çelişir**. Artık özet satırı niyete göre değişiyor; "sadece dolaşmak" niyetinde ise tek bir hedef kategori olmadığı için kategori çeşitliliği gösteriliyor.

10 numaralı hata dürüstlük meselesiydi: panel "bu haftanın özeti" diyor ve "en tatminkâr oturumların öğleden sonra" yazıyordu — oysa prototip tek oturum ölçüyor, haftalık veri diye bir şey yok. "Bu sayı nereden geliyor?" sorusunun cevabı "hiçbir yerden" olacaktı. Artık panel tek oturum ölçtüğünü açıkça yazıyor ve haftalık görünümü gelecek sürüm olarak konumlandırıyor.

**Ortak ders:** 7, 8, 9 ve 10 numaralı hataların dördünü de geliştirici değil, prototipi gerçekten kullanan biri buldu. Bu, raporun kullanıcı testi bölümünde anlatılmaya değer bir bulgudur.

---

## Çoklu niyet seçimi

Kullanıcı aynı anda birden fazla niyet seçebilir. Gerçek hayatta insanlar tek bir ihtiyaçla açmıyor uygulamayı; hem öğrenmek hem kafa dağıtmak isteyebiliyor.

**Kural:** "Sadece dolaşmak" tek başına seçilir. Belirli bir amacın yokken aynı anda belirli bir amacın olduğunu söylemek çelişkilidir. Diğer seçenekler serbestçe birleştirilebilir.

**Skorlama:** Bir gönderinin uyumu, seçilen niyetler içindeki **en iyi eşleşmesidir** — ortalaması değil.

```js
uyum = max( kosinus(gonderi, niyet₁), kosinus(gonderi, niyet₂), ... )
```

Neden maksimum? Kullanıcı "öğrenmek + eğlenmek" dediğinde istediği, hem öğretici hem eğlenceli olan melez gönderiler değil; akışın **her iki ihtiyacı da karşılamasıdır**. Vektörlerin ortalaması alınsaydı saf eğitim içeriği de saf mizah da cezalandırılır, ortada kalan bulanık içerik öne çıkardı. Maksimum alınca saf eğitim 1.0, saf mizah 1.0 alır; çeşitlilik kısıtı da ikisinin akışta birlikte yer almasını sağlar.

**Ölçüm** (`duman_testi.py`, altı ikili kombinasyonun tamamı):

| Kombinasyon | Niyet uyumu | Clickbait | İlk 20'de dağılım |
|---|---|---|---|
| Öğrenmek + Eğlenmek | 0.971 | %0 | 10 / 10 |
| Öğrenmek + Haberdar olmak | 0.975 | %0 | 10 / 10 |
| Öğrenmek + Sosyalleşmek | 0.965 | %0 | 10 / 10 |
| Eğlenmek + Haberdar olmak | 0.969 | %0 | 10 / 10 |
| Eğlenmek + Sosyalleşmek | 0.958 | %0 | 10 / 10 |
| Haberdar olmak + Sosyalleşmek | 0.963 | %0 | 10 / 10 |

Dikkat çeken sonuç: her kombinasyonda ilk 20 gönderi **tam olarak yarı yarıya** bölünüyor. Bu tasarlanmadı, çeşitlilik kısıtından kendiliğinden çıktı — hiçbir niyet diğerini ezmiyor. Ayrıca çoklu seçimde uyum (~0.97) tek niyetli seçimden (~0.80) daha yüksek; beklenen bir sonuç, çünkü havuzda uygun içerik havuzu genişliyor.

Kapanış özeti de her seçilen niyet için ayrı satır gösteriyor, böylece kullanıcı hangi ihtiyacının ne kadar karşılandığını görüyor.

---

## Erişilebilirlik

Şartnamede "erişilebilirlik değerlendirmesi" ayrı bir teslimat. Ölçüm `kontrast_olc.py` ile yapılıyor, sayılar tahmin değil hesaplanmış.

**Palet.** Üç renk: **turkuaz**, **kırmızı**, **beyaz**. Renkler dekoratif değil, anlam taşıyor — turkuaz niyetle hizalı olan her şey (aksan, iyi durum, zaman halkası), kırmızı tuzağın ve pişmanlığın rengi (clickbait rozeti, pişmanlık çubuğu, kötü durum), beyaz da yüzey. Böylece ekranda kırmızı görmek tek başına "burada dikkatin çalınıyor" demek oluyor; kullanıcının etiketi okuması gerekmiyor.

**Bu paletin bilinen zayıflığı.** Turkuaz ve kırmızının bağıl parlaklığı açık temada neredeyse aynı (0.125 ve 0.108, aralarındaki kontrast yalnızca 1.11:1). Yani gri tonlamada veya güçlü renk körlüğünde bu iki renk birbirinden **ayırt edilemez**. Palet göze hoş geldiği için değil, anlamı taşıdığı için seçildi; ama bu zayıflık gerçek ve saklanmıyor.

Telafisi WCAG 1.4.1'in zaten istediği şey: **hiçbir bilgi tek başına renkle taşınmıyor.** Clickbait rozeti "clickbait işareti" yazısını içeriyor, zaman halkasının yanında yüzde yazıyor, seçili niyet hem renkle hem `aria-pressed="true"` ile işaretli. Renk tamamen kaldırılsa da ekran okunabiliyor.

Bu bir niyet beyanı değil, test edilen bir şart: `arayuz_testi.py` akış ekranında `halka-yuzde` öğesini, karşılaştırma ekranında da "clickbait işareti" metnini arıyor. Biri silinirse test kırmızıya döner.

### Belgenin kendisi de denetleniyor

Kontrast ölçümü paletle ilgilidir; belgenin kendisiyle — dil etiketi, karakter kodlaması,
başlık sırası, ARIA geçerliliği, klavye erişimi — ilgili değildir. `erisilebilirlik_testi.py`
bu boşluğu kapatır: 22 kontrol, 8 ekran. Durağan katmanda `pusula.html`'in belge iskeleti ve
üslup dosyası; üretilen katmanda sahte DOM üzerinde çizdirilen yedi ekranın **JavaScript'in
ürettiği** işaret dili incelenir. Kaynak dosyada arama yapmak yeterli değildir; kullanıcının
gördüğü işaret dilini uç anda JavaScript üretir.

| Denetim grubu | Sınanan koşullar | Sonuç |
|---|---|---|
| Belge iskeleti | `<!doctype html>`, `lang="tr"`, `charset=utf-8`, viewport, dolu `<title>`, kapatılmış head/body | 6/6 |
| Üslup (CSS) | `:focus-visible`, `prefers-reduced-motion`, `sr-only`'nin ekran okuyucudan gizlenmemesi, `min()` ile esneyen çerçeve | 4/4 |
| İşaret dili | Geçerli `role` ve `aria-*` adları, `aria-pressed`/`aria-selected` doğru öğede, pozitif `tabindex` yok, düğmelerin erişilebilir adı, `alt` metni, tıklananın `<button>` olması, başlık düzeyi, `role="status"` | 9/9 |
| Renk bağımsızlığı | Zaman halkasında yüzde, clickbait rozetinde metin, seçili niyette `aria-pressed="true"` | 3/3 |

**Bu denetim yazıldığı gün üç sorun buldu.** Prototip `<!doctype html>` ve
`<meta charset="utf-8">` olmadan yayımlanıyordu: belge quirks mode'da açılıyor, karakter
kodlaması tarayıcının tahminine bırakılıyordu. UTF-8 tahmin etmeyen bir ortamda sayfanın
bütün Türkçe harfleri bozuluyordu — hata geliştirme makinesinde görünmediği için uzun süre
fark edilmedi. İkincisi, yan panelde başlık düzeyi h1'den h3'e atlıyordu. Üçüncüsü, sayfa
dili (14 numaralı hatanın çözümü) yalnızca çalışma anında JavaScript ile atanıyordu; artık
işaret dilinin kendisinde duruyor, betik çalışmasa da geçerli. Üçü de düzeltildi.

Ders 13 numaralı hatayla aynı: **ölçmek iddia etmekten farklıdır.** Renkler ölçülüyordu,
belge iskeleti ölçülmüyordu.


**Kontrast (WCAG 2.1 AA).** Renkler önce göze hoş geldiği için seçilmişti; ölçünce açık temada beş çift, koyu temada iki çift eşiğin altında çıktı. Palet turkuaz–kırmızı–beyaza geçirilirken yeni değerler doğrudan ölçülerek seçildi. Kritik çiftlerin son ölçümü:

| Kullanım | Açık tema | Koyu tema | Gereken |
|---|---|---|---|
| Gövde metni | 14.54:1 | 15.10:1 | 4.5:1 |
| İkincil metin (zeminde) | 5.14:1 | 7.34:1 | 4.5:1 |
| Aksan metin / bağlantı | 5.99:1 | 8.18:1 | 4.5:1 |
| Birincil buton yazısı | 5.99:1 | 9.10:1 | 4.5:1 |
| Clickbait rozeti | 5.90:1 | 5.94:1 | 4.5:1 |
| Pişmanlık çubuğu | 6.71:1 | 5.68:1 | 3.0:1 |

Son durum: 14 çiftin tamamı her iki temada AA eşiğini geçiyor, en dar pay 5.05:1 (gerekli 4.5:1). Kenarlıklar WCAG 1.4.11 kapsamı dışında (durum bildirmiyorlar, yüzeyler arka plan farkıyla da ayrılıyor) — ölçülüyor ama eşiğe tabi tutulmuyor; bu ayrım teknik raporda da açıkça belirtilmiştir.

**Diğer önlemler**

- Sayfa dili `tr` olarak işaretli — ekran okuyucu Türkçe metni İngilizce telaffuz etmiyor.
- Akış yeniden sıralandığında `role="status"` canlı bölge tek cümleyle duyuruyor ("Öğrenmek niyetine göre 30 gönderi sıralandı"). Akışın tamamı okunmuyor.
- Renk tek başına bilgi taşımıyor: zaman halkasının yanında yüzde yazıyor, clickbait rozeti metin içeriyor, seçili niyet hem renk hem "seçildi" etiketiyle işaretli.
- Tüm etkileşimli öğelerde görünür `:focus-visible` çerçevesi var.
- `prefers-reduced-motion` destekleniyor: ortam ısınma geçişi ve yumuşak kaydırma kapanıyor.
- Telefon çerçevesi `min()` ile esnek; dar ekranda taşmıyor.

**Henüz yapılmadı:** gerçek ekran okuyucuyla (NVDA/VoiceOver) uçtan uca test, klavye-only tam gezinme denemesi. Faz 3'e planlandı.

---

## Testler neden böyle kurgulandı

Komutlar için yukarıdaki [Testler](#testler) bölümüne bakınız.

`arayuz_testi.py` neden var: `duman_testi.py` yalnızca saf fonksiyonları test ediyordu, çizim kodundaki hatalar yakalanmıyordu. Çoklu niyet eklenirken karşılaştırma modu iki niyet seçilince çöktü ve hiçbir test bunu görmedi (12 numaralı hata). Testin gerçekten çalıştığı, hata bilerek geri konularak doğrulandı — o durumda `COKTU` veriyor.

---

## Dikkat çeken bulgu

Klasik algoritmanın niyet uyumu, niyete göre çarpıcı biçimde değişiyor:

| Niyet | Klasik uyum | PUSULA uyum | Fark |
|---|---|---|---|
| Sadece dolaşmak | 0.557 | 0.737 | +32% |
| Eğlenmek | 0.553 | 0.714 | +29% |
| Haberdar olmak | 0.433 | 0.857 | +98% |
| Öğrenmek | 0.264 | 0.914 | +246% |
| Sosyalleşmek | 0.186 | 0.777 | +318% |

Klasik akış, **eğlenmek** ve **sadece dolaşmak** niyetlerinde PUSULA'ya en yakın sonucu veriyor; **öğrenmek** ve **sosyalleşmek** niyetlerinde ise arada üç-dört kat fark var.

Yorum: bugünkü etkileşim odaklı akışlar pratikte **tek bir niyet ailesine** göre optimize edilmiş durumda — pasif eğlence. Eğlenmek veya vakit geçirmek isteyen kullanıcı zaten iyi hizmet alıyor; öğrenmek, haber almak veya sosyalleşmek isteyen kullanıcı sistematik olarak kötü hizmet alıyor. PUSULA'nın kazancı, mevcut sistemin en çok başarısız olduğu yerde en büyük.

Bu, projenin problem tanımını güçlendiren ve raporda öne çıkarılacak bir bulgudur.

---

## Yapılacaklar

- [x] İçerik havuzu üreteci
- [x] Niyet etiketleme modülü
- [x] Sıralama motoru
- [x] Yan yana karşılaştırma demosu
- [x] Ölçüm ve deney altyapısı
- [x] Kullanıcı araştırması anketi
- [x] UI/UX tasarımları (Niyet Kapısı, akış ekranı, kapanış kartı, refah paneli)
- [x] Çalışan web prototipi (`tasarim/pusula.html`)
- [x] Otomatik doğrulama (`uygulama_uret.py` + `duman_testi.py`)
- [x] Erişilebilirlik denetimi ve WCAG AA kontrast düzeltmeleri
- [x] Kullanıcı araştırması verisinin toplanması ve analizi (n=27)
- [x] Teknik rapor (yarışmaya teslim edildi)
- [ ] Kör A/B testi (etiketler gizli, sıra rastgele) — 15–25 katılımcı
- [ ] Türkçe dil modeliyle etiketleme (sezgisel etiketleyicinin yerine)
- [ ] Memnuniyet geri bildiriminden ödül modeli simülasyonu
- [ ] Tanıtım videosu ve final sunumu
