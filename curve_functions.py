

import numpy as np

def s_curve_min_max_ile(x, min_oran, max_oran, orta_nokta=0.5, diklik=1.0):

    if diklik == 0:
        
        return min_oran + (max_oran - min_oran) * x
    
    
    x_normalized = 2 * (x - orta_nokta)
    
    
    s_curve = np.tanh(diklik * x_normalized)
    
    
    orta_deger = (min_oran + max_oran) / 2
    aralik = (max_oran - min_oran) / 2
    
    return orta_deger + aralik * s_curve

def cap_uygula(degerler, min_cap, max_cap):

    return np.clip(degerler, min_cap, max_cap)

def cift_s_curve_sistemi_yeni(x, 
                             short_min_oran, short_max_oran, short_orta_nokta, short_diklik,
                             long_min_oran, long_max_oran, long_orta_nokta, long_diklik,
                             gecis_genisligi, min_cap, max_cap):

    
    gecis_merkez = 0.5
    gecis_baslangic = gecis_merkez - gecis_genisligi / 2
    gecis_bitis = gecis_merkez + gecis_genisligi / 2
    
    
    short_curve = s_curve_min_max_ile(x, short_min_oran, short_max_oran, 
                                     short_orta_nokta, short_diklik)
    
    
    long_curve = s_curve_min_max_ile(x, long_min_oran, long_max_oran, 
                                    long_orta_nokta, long_diklik)
    
    
    sonuc = np.zeros_like(x)
    
    
    sol_mask = x <= gecis_baslangic
    sonuc[sol_mask] = short_curve[sol_mask]
    
    
    sag_mask = x >= gecis_bitis
    sonuc[sag_mask] = long_curve[sag_mask]
    
    
    orta_mask = (x > gecis_baslangic) & (x < gecis_bitis)
    if np.any(orta_mask):
        
        short_deger = s_curve_min_max_ile(gecis_baslangic, short_min_oran, short_max_oran, 
                                         short_orta_nokta, short_diklik)
        long_deger = s_curve_min_max_ile(gecis_bitis, long_min_oran, long_max_oran, 
                                        long_orta_nokta, long_diklik)
        
        
        t = (x[orta_mask] - gecis_baslangic) / gecis_genisligi
        sonuc[orta_mask] = short_deger + t * (long_deger - short_deger)
    
    
    sonuc = cap_uygula(sonuc, min_cap, max_cap)
    short_curve = cap_uygula(short_curve, min_cap, max_cap)
    long_curve = cap_uygula(long_curve, min_cap, max_cap)
    
    return sonuc, short_curve, long_curve

def belirli_pozisyondaki_funding_hesapla(pozisyon, parametreler):

    x = np.array([pozisyon])
    funding, _, _ = cift_s_curve_sistemi_yeni(
        x,
        parametreler['short_min_oran'], parametreler['short_max_oran'], 
        parametreler['short_orta_nokta'], parametreler['short_diklik'],
        parametreler['long_min_oran'], parametreler['long_max_oran'], 
        parametreler['long_orta_nokta'], parametreler['long_diklik'],
        parametreler['gecis_genisligi'], parametreler['min_cap'], parametreler['max_cap']
    )
    
    
    funding_bolgeleri = parametreler.get('funding_bolgeleri', [])
    saat_dilimi = 8  
    
    for bolge in funding_bolgeleri:
        if bolge['baslangic'] <= pozisyon <= bolge['bitis']:
            saat_dilimi = bolge['saat']
            break
    
    return funding[0], saat_dilimi

def funding_oran_hesaplamalari(funding_orani_per_period, saat_dilimi):

    
    gunluk_kesim_sayisi = 24 / saat_dilimi
    
    
    gunluk_oran = funding_orani_per_period * gunluk_kesim_sayisi
    
    
    yillik_oran = gunluk_oran * 365
    
    
    saatlik_equivalent = funding_orani_per_period / saat_dilimi
    
    return {
        'saat_dilimi': saat_dilimi,
        'saat_dilimi_orani': funding_orani_per_period,  
        'gunluk_kesim_sayisi': gunluk_kesim_sayisi,
        'gunluk_oran': gunluk_oran,
        'yillik_oran': yillik_oran,
        'saatlik_equivalent': saatlik_equivalent
    }

def funding_oran_hesaplamalari_dinamik(funding_orani_per_period, saat_dilimi, pozisyon):

    try:
        
        funding_orani = float(funding_orani_per_period)
        saat = float(saat_dilimi)
        pos = float(pozisyon)
        
        
        if saat <= 0:
            saat = 8.0  
            
        
        
        gunluk_kesim_sayisi = 24.0 / saat
        
        
        gunluk_oran = funding_orani * gunluk_kesim_sayisi
        
        
        yillik_oran = gunluk_oran * 365.0
        
        
        saatlik_equivalent = funding_orani / saat
        
        return {
            'saat_dilimi': int(saat),
            'saat_dilimi_orani': funding_orani,  
            'gunluk_kesim_sayisi': gunluk_kesim_sayisi,
            'gunluk_oran': gunluk_oran,
            'yillik_oran': yillik_oran,
            'saatlik_equivalent': saatlik_equivalent,
            'pozisyon': pos
        }
        
    except (TypeError, ValueError, ZeroDivisionError) as e:
        print(f"Hesaplama hatası: {e}")
        
        return {
            'saat_dilimi': 8,
            'saat_dilimi_orani': 0.0,
            'gunluk_kesim_sayisi': 3.0,
            'gunluk_oran': 0.0,
            'yillik_oran': 0.0,
            'saatlik_equivalent': 0.0,
            'pozisyon': 0.5
        }

def sistem_istatistiklerini_hesapla_yeni(funding_oranlari):

    istatistikler = {
        'min': float(funding_oranlari.min()),
        'max': float(funding_oranlari.max()),
        'ortalama': float(funding_oranlari.mean()),
        'standart_sapma': float(funding_oranlari.std()),
        'aralik': float(funding_oranlari.max() - funding_oranlari.min())
    }
    
    return istatistikler

def gecis_bolgesi_bilgilerini_hesapla(parametreler):

    gecis_merkez = 0.5
    gecis_baslangic = gecis_merkez - parametreler['gecis_genisligi'] / 2
    gecis_bitis = gecis_merkez + parametreler['gecis_genisligi'] / 2
    
    return {
        'merkez': gecis_merkez,
        'baslangic': gecis_baslangic,
        'bitis': gecis_bitis,
        'genislik': parametreler['gecis_genisligi']
    }

def parametreleri_dogrula_yeni(parametreler):

    hatalar = []
    
    
    for anahtar in ['short_diklik', 'long_diklik']:
        if parametreler.get(anahtar, 0) < 0:
            hatalar.append(f"{anahtar} negatif olamaz")
    
    
    for anahtar in ['short_orta_nokta', 'long_orta_nokta']:
        deger = parametreler.get(anahtar, 0.5)
        if deger < 0 or deger > 1:
            hatalar.append(f"{anahtar} 0-1 arasında olmalı")
    
    
    short_min = parametreler.get('short_min_oran', 0)
    short_max = parametreler.get('short_max_oran', 0)
    if short_min >= short_max:
        hatalar.append("Short min oran < Short max oran olmalı")
    
    
    long_min = parametreler.get('long_min_oran', 0)
    long_max = parametreler.get('long_max_oran', 0)
    if long_min >= long_max:
        hatalar.append("Long min oran < Long max oran olmalı")
    
    
    min_cap = parametreler.get('min_cap', -1)
    max_cap = parametreler.get('max_cap', 1)
    if min_cap >= max_cap:
        hatalar.append("Min cap < Max cap olmalı")
    
    
    if parametreler.get('gecis_genisligi', 0.2) <= 0:
        hatalar.append("Geçiş genişliği pozitif olmalı")
    
    
    if parametreler.get('cozunurluk', 500) < 50:
        hatalar.append("Çözünürlük en az 50 olmalı")
    
    return hatalar

def duyarlilik_analizi_uret_yeni(temel_parametreler, parametre_ismi, varyasyon_araligi, x_degerleri):

    sonuclar = {}
    
    for varyasyon in varyasyon_araligi:
        
        test_parametreleri = temel_parametreler.copy()
        test_parametreleri[parametre_ismi] = varyasyon
        
        
        funding_degerleri, _, _ = cift_s_curve_sistemi_yeni(
            x_degerleri, 
            test_parametreleri['short_min_oran'], test_parametreleri['short_max_oran'],
            test_parametreleri['short_orta_nokta'], test_parametreleri['short_diklik'],
            test_parametreleri['long_min_oran'], test_parametreleri['long_max_oran'],
            test_parametreleri['long_orta_nokta'], test_parametreleri['long_diklik'],
            test_parametreleri['gecis_genisligi'], test_parametreleri['min_cap'], test_parametreleri['max_cap']
        )
        
        sonuclar[varyasyon] = funding_degerleri
    
    return sonuclar

def test_senaryolari_uret_yeni(x_degerleri):

    senaryolar = {
        'Lineer Artış': np.linspace(-0.5, 0.5, len(x_degerleri)),
        'Sabit Değer': np.full_like(x_degerleri, 0.1),
        'Adım Fonksiyonu': np.where(x_degerleri > 0.5, 0.3, -0.3),
        'Sinüs Dalgası': 0.2 * np.sin(x_degerleri * 4 * np.pi)
    }
    
    return senaryolar

def cap_etkisi_analizi(x_degerleri, parametreler, orijinal_min_cap, orijinal_max_cap):

    orijinal_params = parametreler.copy()
    orijinal_params['min_cap'] = -10.0  
    orijinal_params['max_cap'] = 10.0
    
    orijinal_curve, _, _ = cift_s_curve_sistemi_yeni(
        x_degerleri,
        orijinal_params['short_min_oran'], orijinal_params['short_max_oran'],
        orijinal_params['short_orta_nokta'], orijinal_params['short_diklik'],
        orijinal_params['long_min_oran'], orijinal_params['long_max_oran'],
        orijinal_params['long_orta_nokta'], orijinal_params['long_diklik'],
        orijinal_params['gecis_genisligi'], orijinal_params['min_cap'], orijinal_params['max_cap']
    )
    
    
    capli_curve, _, _ = cift_s_curve_sistemi_yeni(
        x_degerleri,
        parametreler['short_min_oran'], parametreler['short_max_oran'],
        parametreler['short_orta_nokta'], parametreler['short_diklik'],
        parametreler['long_min_oran'], parametreler['long_max_oran'],
        parametreler['long_orta_nokta'], parametreler['long_diklik'],
        parametreler['gecis_genisligi'], orijinal_min_cap, orijinal_max_cap
    )
    
    
    min_kesilen = np.sum(orijinal_curve < orijinal_min_cap)
    max_kesilen = np.sum(orijinal_curve > orijinal_max_cap)
    
    return {
        'orijinal_curve': orijinal_curve,
        'capli_curve': capli_curve,
        'min_kesilen_nokta': min_kesilen,
        'max_kesilen_nokta': max_kesilen,
        'toplam_kesilen': min_kesilen + max_kesilen,
        'toplam_nokta': len(x_degerleri)
    }

def funding_bolgeleri_analizi(funding_bolgeleri, parametreler):

    analizler = []
    
    for bolge in funding_bolgeleri:
        
        orta_pozisyon = (bolge['baslangic'] + bolge['bitis']) / 2
        funding_orani, _ = belirli_pozisyondaki_funding_hesapla(orta_pozisyon, parametreler)
        
        
        hesaplamalar = funding_oran_hesaplamalari_dinamik(funding_orani, bolge['saat'], orta_pozisyon)
        
        analizler.append({
            'bolge': bolge,
            'funding_orani': funding_orani,
            'hesaplamalar': hesaplamalar
        })
    
    return analizler