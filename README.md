# Dinamik Funding Fee Sistemi

## Genel Bakış

Bu uygulama kripto para borsaları için gelişmiş bir funding fee yönetim sistemidir. Geleneksel sabit funding oranlarının aksine, piyasa pozisyonlarına göre dinamik olarak değişen oranlar ve kesim sıklıkları sunar.

## Sistem Özellikleri

### Ana Özellikler
- Pozisyona dayalı dinamik funding oranları
- Ekstrem pozisyonlarda artırılmış kesim sıklığı

### Teknik Özellikler
- Çift S-curve algoritması ile optimize edilmiş funding hesaplama (long ve short için ayrı s-curve)
- Cap ve sınır değer kontrolü
- Dinamik geçiş bölgesi ayarları


## Nasıl Çalışır

### Temel Mantık

1. **Pozisyon Analizi**: Sistemde 0.0 tam short, 1.0 tam long pozisyonu temsil eder, long short oranları toplam pozisyon büyüklüğünün birbirine oranı şeklinde hesaplanmalıdır, yani 0.5 toplam short pozisyon büyüklüklerinin long pozisyon büyüklüğüne eşit olduğunu gösterir. 
2. **Dinamik Bölgeler**: Her pozisyon aralığında farklı funding sıklığı ve oranı uygulanır
3. **S-Curve Hesaplama**: Yumuşak geçişler için matematiksel S-curve fonksiyonu kullanılır
4. **Geçiş Bölgesi**: Orta bölgede lineer interpolasyon ile yumuşak geçiş sağlanır

### Funding Bölgeleri
Funding bölgeleri o long/short oranı için 
## Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.8 veya üzeri
- Streamlit 1.28.0+
- Plotly 5.15.0+
- Pandas 2.0.0+
- NumPy 1.24.0+

### Kurulum Adımları

1. Projeyi klonlayın veya dosyaları indirin
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
3. Uygulamayı başlatın:
   ```bash
   python run.py
   ```
   veya
   ```bash
   streamlit run main.py
   ```

### Otomatik Kurulum
`run.py` dosyası eksik kütüphaneleri otomatik olarak tespit edip yükleme önerisi sunar.

## Kullanım

### Temel Kullanım

1. Uygulamayı başlattıktan sonra web tarayıcısında açılan arayüze gidin
2. Sol panelden parametreleri ayarlayın
3. Ana grafikte funding eğrisini görüntüleyin
4. Pozisyon slider ile farklı pozisyonlardaki funding değerlerini test edin
5. İstatistikler ve analiz sonuçlarını inceleyin

### Senaryo Yönetimi

- **Yeni Senaryo**: Sol panelden parametreleri ayarlayıp isim vererek kaydedin
- **Senaryo Yükleme**: Kaydedilmiş senaryoları dropdown menüden seçin
- **Hızlı Kaydetme**: Mevcut senaryoyu hızla güncelleyin
- **Default Yapma**: Senaryoyu sistem başlangıcında otomatik yüklenecek şekilde ayarlayın

### JSON İşlemleri

- **Export**: Mevcut konfigürasyonu JSON dosyası olarak indirin
- **Import**: Önceden kaydedilmiş JSON dosyasını yükleyin
- **Settings.json**: Sistem varsayılan ayarlarını yönetin

## Borsa Entegrasyonu

NEXTMONEY entegrasyonu için ilk önce toplam pozisyon büyüklüklerinin oranı bulunmalıdır.

Daha sonrasında, o an seçilmiş olan ayarlara göre fonlama bedeli ve sıklığı bulunabilir

Fonlama bedelleri belirtilen fonlama süresinin sonunda kesilir, sıklık arttıkça bir gün içindeki kesilen fonlama sayısı artmış olur.

Kesilmesi gereken fonlama bedeli kesim süresinin sonundaki dakikadaki pozisyon oranlarına göre yapılır.

Fonlama süresi ise bir önceki fonlama döneminde süre değişimi tetiklenirse bir sonraki döneme etki edecek şekilde işler.
Yani 8 saate bir fonlama yapılıyordu fakat, kesilen fonlama döneminde yüksek bir long oranı yaşandı diyelim. Bu noktada 8 saatin sonunda kesilen fonlama doğal olarak yüksek olacak ama aynı zamanda bir sonraki fonlama için saat de yine burda belirlenecek. Eğer daha düşük bir fonlama dilimine girildiyse bir sonraki fonlama kesintisi o saat geldiğinde yapılacak.

