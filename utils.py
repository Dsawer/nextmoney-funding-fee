

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from config import HAZIR_MODLAR, ARAYUZ_AYARLARI, AYAR_DOSYA_YOLU

def hazir_mod_yukle(mod_ismi):

    if mod_ismi in HAZIR_MODLAR:
        return HAZIR_MODLAR[mod_ismi].copy()
    return None

def kayitli_ayarlari_yukle():

    try:
        if os.path.exists(AYAR_DOSYA_YOLU):
            with open(AYAR_DOSYA_YOLU, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"Ayarlar yüklenirken hata: {e}")
        return {}

def kayitli_ayarlari_kaydet(ayarlar):

    try:
        with open(AYAR_DOSYA_YOLU, 'w', encoding='utf-8') as f:
            json.dump(ayarlar, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Ayarlar kaydedilirken hata: {e}")
        return False

def yeni_ayar_kaydet(ayar_ismi, parametreler):

    kayitli_ayarlar = kayitli_ayarlari_yukle()
    
    kayitli_ayarlar[ayar_ismi] = {
        'isim': ayar_ismi,
        'kayit_tarihi': datetime.now().isoformat(),
        'parametreler': parametreler.copy()
    }
    
    return kayitli_ayarlari_kaydet(kayitli_ayarlar)

def ayar_sil(ayar_ismi):

    kayitli_ayarlar = kayitli_ayarlari_yukle()
    
    if ayar_ismi in kayitli_ayarlar:
        del kayitli_ayarlar[ayar_ismi]
        return kayitli_ayarlari_kaydet(kayitli_ayarlar)
    
    return False

def konfigurasyonu_dict_olarak_export_et(parametreler):

    konfig = {
        'sistem_versiyonu': '2.0',
        'olusturulma_tarihi': datetime.now().isoformat(),
        'parametreler': {
            'short_min_oran': parametreler.get('short_min_oran', -0.3),
            'short_max_oran': parametreler.get('short_max_oran', 0.0),
            'short_orta_nokta': parametreler.get('short_orta_nokta', 0.2),
            'short_diklik': parametreler.get('short_diklik', 2.0),
            'long_min_oran': parametreler.get('long_min_oran', 0.0),
            'long_max_oran': parametreler.get('long_max_oran', 0.3),
            'long_orta_nokta': parametreler.get('long_orta_nokta', 0.8),
            'long_diklik': parametreler.get('long_diklik', 2.0),
            'gecis_genisligi': parametreler.get('gecis_genisligi', 0.2),
            'min_cap': parametreler.get('min_cap', -0.5),
            'max_cap': parametreler.get('max_cap', 0.5),
            'cozunurluk': parametreler.get('cozunurluk', 500)
        },
        'funding_bolgeleri': parametreler.get('funding_bolgeleri', []),
        'funding_saatleri': parametreler.get('funding_saatleri', [1, 4, 8, 12, 24]),
        'kritik_seviyeler': parametreler.get('kritik_seviyeler', {}),
        'metadata': {
            'aciklama': 'Funding Fee Sistemi v2.0 - Gelişmiş parametre sistemi',
            'pozisyon_aciklama': '0.0 = Tam Short, 1.0 = Tam Long'
        }
    }
    return konfig

def dict_ten_konfigurasyon_import_et(konfig_dict):

    parametreler = {}
    
    if 'parametreler' in konfig_dict:
        parametreler.update(konfig_dict['parametreler'])
    
    if 'funding_bolgeleri' in konfig_dict:
        parametreler['funding_bolgeleri'] = konfig_dict['funding_bolgeleri']
    
    if 'funding_saatleri' in konfig_dict:
        parametreler['funding_saatleri'] = konfig_dict['funding_saatleri']
    
    if 'kritik_seviyeler' in konfig_dict:
        parametreler['kritik_seviyeler'] = konfig_dict['kritik_seviyeler']
    
    return parametreler

def parametre_tablosu_olustur_yeni(parametreler):

    veri = {
        'Parametre Grubu': [],
        'Parametre': [],
        'Değer': [],
        'Açıklama': []
    }
    
    
    short_parametreleri = [
        ('Short Eğrisi', 'Min Oran', parametreler.get('short_min_oran', -0.3), 'En düşük short funding oranı'),
        ('Short Eğrisi', 'Max Oran', parametreler.get('short_max_oran', 0.0), 'En yüksek short funding oranı'),
        ('Short Eğrisi', 'Orta Nokta', parametreler.get('short_orta_nokta', 0.2), 'S-eğrisinin merkez pozisyonu'),
        ('Short Eğrisi', 'Diklik', parametreler.get('short_diklik', 2.0), 'Eğrinin keskinliği (0=lineer)'),
    ]
    
    
    long_parametreleri = [
        ('Long Eğrisi', 'Min Oran', parametreler.get('long_min_oran', 0.0), 'En düşük long funding oranı'),
        ('Long Eğrisi', 'Max Oran', parametreler.get('long_max_oran', 0.3), 'En yüksek long funding oranı'),
        ('Long Eğrisi', 'Orta Nokta', parametreler.get('long_orta_nokta', 0.8), 'S-eğrisinin merkez pozisyonu'),
        ('Long Eğrisi', 'Diklik', parametreler.get('long_diklik', 2.0), 'Eğrinin keskinliği (0=lineer)'),
    ]
    
    
    sistem_parametreleri = [
        ('Sistem', 'Geçiş Genişliği', parametreler.get('gecis_genisligi', 0.2), 'İki eğri arası karışım bölgesi'),
        ('Sistem', 'Min Cap', parametreler.get('min_cap', -0.5), 'Minimum funding sınırı'),
        ('Sistem', 'Max Cap', parametreler.get('max_cap', 0.5), 'Maksimum funding sınırı'),
        ('Sistem', 'Çözünürlük', parametreler.get('cozunurluk', 500), 'Grafik hassasiyeti')
    ]
    
    tum_parametreler = short_parametreleri + long_parametreleri + sistem_parametreleri
    
    for grup, parametre, deger, aciklama in tum_parametreler:
        veri['Parametre Grubu'].append(grup)
        veri['Parametre'].append(parametre)
        if isinstance(deger, float):
            veri['Değer'].append(f"{deger:.6f}")
        else:
            veri['Değer'].append(str(deger))
        veri['Açıklama'].append(aciklama)
    
    return pd.DataFrame(veri)

def funding_saatleri_tablosu_olustur(funding_saatleri):
    """
    Funding saatlerini tablo formatında döndürür
    """
    veri = {
        'Saat Dilimi': [f"{saat} Saat" for saat in funding_saatleri],
        'Günde Kaç Kez': [24 // saat for saat in funding_saatleri],
        'Haftalık': [7 * (24 // saat) for saat in funding_saatleri],
        'Aylık (30 gün)': [30 * (24 // saat) for saat in funding_saatleri]
    }
    
    return pd.DataFrame(veri)

def kritik_seviyeler_tablosu_olustur_yeni(kritik_seviyeler):

    if not kritik_seviyeler:
        return pd.DataFrame({'Pozisyon': [], 'Etiket': [], 'Bölge': []})
    
    veri = {
        'Pozisyon': [f"{pos:.3f}" for pos in kritik_seviyeler.keys()],
        'Etiket': list(kritik_seviyeler.values()),
        'Bölge': []
    }
    
    
    for pos in kritik_seviyeler.keys():
        if pos < 0.3:
            veri['Bölge'].append('🔴 Short Bölgesi')
        elif pos > 0.7:
            veri['Bölge'].append('🟢 Long Bölgesi')
        else:
            veri['Bölge'].append('🟡 Nötr Bölge')
    
    return pd.DataFrame(veri)

def sayiyi_formatla(deger, ondalik=6):

    if abs(deger) < 1e-10:
        return "0.000000"
    return f"{deger:.{ondalik}f}"

def indirme_verisi_olustur_yeni(parametreler, x_degerleri, funding_oranlari):

    indirme_verisi = {
        'konfigurasyon': konfigurasyonu_dict_olarak_export_et(parametreler),
        'sonuclar': {
            'x_degerleri': x_degerleri.tolist(),
            'funding_oranlari': funding_oranlari.tolist()
        },
        'metadata': {
            'olusturulma_tarihi': datetime.now().isoformat(),
            'veri_noktasi_sayisi': len(x_degerleri),
            'x_araligi': [0.0, 1.0],
            'sistem_versiyonu': '2.0',
            'aciklama': 'Funding Fee Sistemi v2.0 - 0.0 = Tam Short, 1.0 = Tam Long'
        }
    }
    
    return indirme_verisi

def pozisyon_aciklamasi_al(pozisyon_degeri):

    if pozisyon_degeri < 0.1:
        return "🔴 Ekstrem Short Pozisyon"
    elif pozisyon_degeri < 0.3:
        return "🟠 Güçlü Short Pozisyon"
    elif pozisyon_degeri < 0.4:
        return "🟡 Orta Short Pozisyon" 
    elif pozisyon_degeri < 0.6:
        return "⚪ Nötr Pozisyon"
    elif pozisyon_degeri < 0.7:
        return "🟡 Orta Long Pozisyon"
    elif pozisyon_degeri < 0.9:
        return "🟢 Güçlü Long Pozisyon"
    else:
        return "🟢 Ekstrem Long Pozisyon"

def funding_orani_risk_seviyesi(oran):
 
    abs_oran = abs(oran)
    if abs_oran < 0.05:
        return "🟢 Düşük Risk"
    elif abs_oran < 0.15:
        return "🟡 Orta Risk"
    elif abs_oran < 0.30:
        return "🟠 Yüksek Risk"
    else:
        return "🔴 Çok Yüksek Risk"

def sistem_performans_metrikleri_yeni(funding_oranlari, parametreler):

    abs_ortalama = np.mean(np.abs(funding_oranlari))
    standart_sapma = np.std(funding_oranlari)
    
    metrikler = {
        'etkinlik_skoru': abs_ortalama / (standart_sapma + 1e-8),
        'denge_skoru': 1 - abs(np.mean(funding_oranlari)) / (standart_sapma + 1e-8),
        'stabilite_skoru': 1 / (standart_sapma + 1e-8),
        'dinamik_aralik': np.max(funding_oranlari) - np.min(funding_oranlari),
        'cap_kullanim_orani': (np.sum(funding_oranlari >= parametreler['max_cap']) + 
                              np.sum(funding_oranlari <= parametreler['min_cap'])) / len(funding_oranlari)
    }
    
    
    for anahtar in ['etkinlik_skoru', 'denge_skoru', 'stabilite_skoru']:
        metrikler[anahtar] = min(100, max(0, metrikler[anahtar] * 10))
    
    metrikler['cap_kullanim_orani'] *= 100  
    
    return metrikler

def gecis_bolgesi_analizi(x_degerleri, funding_oranlari, gecis_bilgileri):

    gecis_maskesi = ((x_degerleri >= gecis_bilgileri['baslangic']) & 
                     (x_degerleri <= gecis_bilgileri['bitis']))
    
    if not np.any(gecis_maskesi):
        return None
    
    gecis_funding = funding_oranlari[gecis_maskesi]
    gecis_x = x_degerleri[gecis_maskesi]
    
    
    if len(gecis_funding) > 1:
        gradyan = np.gradient(gecis_funding, gecis_x)
        max_gradyan = np.max(np.abs(gradyan))
        ortalama_gradyan = np.mean(np.abs(gradyan))
    else:
        max_gradyan = 0
        ortalama_gradyan = 0
    
    analiz = {
        'nokta_sayisi': len(gecis_funding),
        'min_funding': float(np.min(gecis_funding)),
        'max_funding': float(np.max(gecis_funding)),
        'funding_aralik': float(np.max(gecis_funding) - np.min(gecis_funding)),
        'max_gradyan': float(max_gradyan),
        'ortalama_gradyan': float(ortalama_gradyan),
        'puruzsuzluk_skoru': float(1 / (1 + np.var(gradyan) if len(gecis_funding) > 1 else 1))
    }
    
    return analiz

def json_dosyasi_dogrula(json_data):

    gerekli_alanlar = [
        'parametreler',
        'sistem_versiyonu'
    ]
    
    for alan in gerekli_alanlar:
        if alan not in json_data:
            return False, f"Gerekli alan eksik: {alan}"
    
    
    parametreler = json_data.get('parametreler', {})
    gerekli_parametreler = [
        'short_min_oran', 'short_max_oran', 'short_orta_nokta', 'short_diklik',
        'long_min_oran', 'long_max_oran', 'long_orta_nokta', 'long_diklik',
        'gecis_genisligi', 'min_cap', 'max_cap'
    ]
    
    for param in gerekli_parametreler:
        if param not in parametreler:
            return False, f"Gerekli parametre eksik: {param}"
    
    return True, "Geçerli"

def ozel_ayar_isimleri_listesi():

    kayitli_ayarlar = kayitli_ayarlari_yukle()
    return list(kayitli_ayarlar.keys())

def varsayilan_ayarlari_yukle():
    """
    Sistem varsayılan ayarlarını döndürür
    """
    return {
        'short_min_oran': -0.010000,
        'short_max_oran': 0.000000,
        'short_orta_nokta': 0.200000,
        'short_diklik': 2.500000,
        'long_min_oran': 0.000000,
        'long_max_oran': 0.010000,
        'long_orta_nokta': 0.800000,
        'long_diklik': 2.500000,
        'gecis_genisligi': 0.150000,
        'min_cap': -0.750000,
        'max_cap': 0.750000,
        'cozunurluk': 500,
        'funding_bolgeleri': [
            {'baslangic': 0.000000, 'bitis': 0.200000, 'saat': 1, 'etiket': 'Ekstrem Short'},
            {'baslangic': 0.200000, 'bitis': 0.400000, 'saat': 2, 'etiket': 'Short'},
            {'baslangic': 0.400000, 'bitis': 0.600000, 'saat': 8, 'etiket': 'Normal'},
            {'baslangic': 0.600000, 'bitis': 0.800000, 'saat': 2, 'etiket': 'Long'},
            {'baslangic': 0.800000, 'bitis': 1.000000, 'saat': 1, 'etiket': 'Ekstrem Long'}
        ],
        'funding_saatleri': [8],
        'kritik_seviyeler': {}
    }


def coklu_senaryo_yukle():

    try:
        if os.path.exists("settings.json"):
            with open("settings.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('senaryolar', {})
        return {}
    except Exception as e:
        st.error(f"Senaryolar yüklenirken hata: {e}")
        return {}

def coklu_senaryo_kaydet(senaryolar):

    try:
        
        settings_data = {
            "sistem_versiyonu": "2.0",
            "olusturulma_tarihi": datetime.now().isoformat(),
            "senaryolar": senaryolar,
            "metadata": {
                "aciklama": "Funding Fee Sistemi Senaryolar",
                "senaryo_sayisi": len(senaryolar),
                "son_guncelleme": datetime.now().strftime('%Y-%m-%d'),
                "kullanim": "Senaryo ismi ile doğrudan yüklenebilir"
            }
        }
        
        with open("settings.json", 'w', encoding='utf-8') as f:
            json.dump(settings_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Senaryolar kaydedilirken hata: {e}")
        return False

def yeni_senaryo_ekle(senaryo_ismi, parametreler, aciklama=""):

    senaryolar = coklu_senaryo_yukle()
    
    senaryolar[senaryo_ismi] = {
        "isim": senaryo_ismi,
        "aciklama": aciklama if aciklama else f"Özel senaryo - {senaryo_ismi}",
        "kayit_tarihi": datetime.now().isoformat(),
        "parametreler": parametreler.copy()
    }
    
    return coklu_senaryo_kaydet(senaryolar)

def senaryo_sil(senaryo_ismi):

    senaryolar = coklu_senaryo_yukle()
    
    if senaryo_ismi in senaryolar:
        del senaryolar[senaryo_ismi]
        return coklu_senaryo_kaydet(senaryolar)
    
    return False

def senaryo_isimleri_listesi():

    senaryolar = coklu_senaryo_yukle()
    return list(senaryolar.keys())

def senaryo_yukle(senaryo_ismi):

    senaryolar = coklu_senaryo_yukle()
    if senaryo_ismi in senaryolar:
        senaryo = senaryolar[senaryo_ismi]
        return senaryo.get('parametreler', {})
    return None

def json_dosyasi_dogrula_coklu(json_data):

    if 'senaryolar' in json_data:
        
        senaryolar = json_data.get('senaryolar', {})
        if not senaryolar:
            return False, "Hiç senaryo bulunamadı"
        
        for senaryo_ismi, senaryo in senaryolar.items():
            if 'parametreler' not in senaryo:
                return False, f"Senaryo '{senaryo_ismi}' parametreleri eksik"
                
        return True, f"{len(senaryolar)} senaryo bulundu"
    
    elif 'parametreler' in json_data:
        
        return True, "Tek senaryo formatı (eski format)"
    
    else:
        return False, "Geçersiz JSON formatı"

def dict_ten_coklu_senaryo_import_et(json_data):

    if 'senaryolar' in json_data:
        return json_data['senaryolar']
    elif 'parametreler' in json_data:
        
        return {
            'Imported_Scenario': {
                'isim': 'İçe Aktarılan Senaryo',
                'aciklama': 'Eski formatdan import edildi',
                'parametreler': json_data['parametreler'],
                'funding_bolgeleri': json_data.get('funding_bolgeleri', [])
            }
        }
    return {}

def settings_json_olustur_default():

    default_senaryolar = {
        "Binance_Default": {
            "isim": "Default Style",
            "aciklama": "tarzı dinamik funding sistemi",
            "parametreler": {
                "short_min_oran": -0.010000,
                "short_max_oran": 0.000000,
                "short_orta_nokta": 0.200000,
                "short_diklik": 2.500000,
                "long_min_oran": 0.000000,
                "long_max_oran": 0.010000,
                "long_orta_nokta": 0.800000,
                "long_diklik": 2.500000,
                "gecis_genisligi": 0.050000,
                "min_cap": -0.750000,
                "max_cap": 0.750000,
                "funding_bolgeleri": [
                    {"baslangic": 0.000000, "bitis": 0.100000, "saat": 1, "etiket": "Ekstrem Short (1h)"},
                    {"baslangic": 0.100000, "bitis": 0.300000, "saat": 2, "etiket": "Yüksek Short (2h)"},
                    {"baslangic": 0.300000, "bitis": 0.450000, "saat": 4, "etiket": "Orta Short (4h)"},
                    {"baslangic": 0.450000, "bitis": 0.550000, "saat": 8, "etiket": "Normal (8h)"},
                    {"baslangic": 0.550000, "bitis": 0.700000, "saat": 4, "etiket": "Orta Long (4h)"},
                    {"baslangic": 0.700000, "bitis": 0.900000, "saat": 2, "etiket": "Yüksek Long (2h)"},
                    {"baslangic": 0.900000, "bitis": 1.000000, "saat": 1, "etiket": "Ekstrem Long (1h)"}
                ]
            }
        },
        "Aggressive_Style": {
            "isim": "Agresif Funding Sistemi",
            "aciklama": "Yüksek funding oranları ile agresif yaklaşım",
            "parametreler": {
                "short_min_oran": -0.025000,
                "short_max_oran": 0.000000,
                "short_orta_nokta": 0.150000,
                "short_diklik": 3.000000,
                "long_min_oran": 0.000000,
                "long_max_oran": 0.025000,
                "long_orta_nokta": 0.850000,
                "long_diklik": 3.000000,
                "gecis_genisligi": 0.100000,
                "min_cap": -1.000000,
                "max_cap": 1.000000,
                "funding_bolgeleri": [
                    {"baslangic": 0.000000, "bitis": 0.150000, "saat": 1, "etiket": "Ultra Short (1h)"},
                    {"baslangic": 0.150000, "bitis": 0.350000, "saat": 3, "etiket": "Strong Short (3h)"},
                    {"baslangic": 0.350000, "bitis": 0.650000, "saat": 8, "etiket": "Normal (8h)"},
                    {"baslangic": 0.650000, "bitis": 0.850000, "saat": 3, "etiket": "Strong Long (3h)"},
                    {"baslangic": 0.850000, "bitis": 1.000000, "saat": 1, "etiket": "Ultra Long (1h)"}
                ]
            }
        },
        "Conservative_Style": {
            "isim": "Konservatif Funding Sistemi",
            "aciklama": "Düşük funding oranları ile yumuşak yaklaşım",
            "parametreler": {
                "short_min_oran": -0.005000,
                "short_max_oran": 0.000000,
                "short_orta_nokta": 0.250000,
                "short_diklik": 1.500000,
                "long_min_oran": 0.000000,
                "long_max_oran": 0.005000,
                "long_orta_nokta": 0.750000,
                "long_diklik": 1.500000,
                "gecis_genisligi": 0.200000,
                "min_cap": -0.300000,
                "max_cap": 0.300000,
                "funding_bolgeleri": [
                    {"baslangic": 0.000000, "bitis": 0.200000, "saat": 4, "etiket": "Short Zone (4h)"},
                    {"baslangic": 0.200000, "bitis": 0.300000, "saat": 6, "etiket": "Mid Short (6h)"},
                    {"baslangic": 0.300000, "bitis": 0.700000, "saat": 8, "etiket": "Normal (8h)"},
                    {"baslangic": 0.700000, "bitis": 0.800000, "saat": 6, "etiket": "Mid Long (6h)"},
                    {"baslangic": 0.800000, "bitis": 1.000000, "saat": 4, "etiket": "Long Zone (4h)"}
                ]
            }
        },
        "High_Frequency": {
            "isim": "Yüksek Frekans Sistemi",
            "aciklama": "Çok sık funding kesintileri ile hızlı dengeleme",
            "parametreler": {
                "short_min_oran": -0.008000,
                "short_max_oran": 0.000000,
                "short_orta_nokta": 0.200000,
                "short_diklik": 4.000000,
                "long_min_oran": 0.000000,
                "long_max_oran": 0.008000,
                "long_orta_nokta": 0.800000,
                "long_diklik": 4.000000,
                "gecis_genisligi": 0.080000,
                "min_cap": -0.500000,
                "max_cap": 0.500000,
                "funding_bolgeleri": [
                    {"baslangic": 0.000000, "bitis": 0.200000, "saat": 1, "etiket": "Hyper Short (1h)"},
                    {"baslangic": 0.200000, "bitis": 0.400000, "saat": 2, "etiket": "Fast Short (2h)"},
                    {"baslangic": 0.400000, "bitis": 0.600000, "saat": 4, "etiket": "Normal (4h)"},
                    {"baslangic": 0.600000, "bitis": 0.800000, "saat": 2, "etiket": "Fast Long (2h)"},
                    {"baslangic": 0.800000, "bitis": 1.000000, "saat": 1, "etiket": "Hyper Long (1h)"}
                ]
            }
        },
        "Linear_Simple": {
            "isim": "Basit Lineer Sistem",
            "aciklama": "Lineer funding oranları - basit yaklaşım",
            "parametreler": {
                "short_min_oran": -0.015000,
                "short_max_oran": 0.000000,
                "short_orta_nokta": 0.250000,
                "short_diklik": 0.000000,
                "long_min_oran": 0.000000,
                "long_max_oran": 0.015000,
                "long_orta_nokta": 0.750000,
                "long_diklik": 0.000000,
                "gecis_genisligi": 0.000000,
                "min_cap": -0.500000,
                "max_cap": 0.500000,
                "funding_bolgeleri": [
                    {"baslangic": 0.000000, "bitis": 0.400000, "saat": 4, "etiket": "Short Region (4h)"},
                    {"baslangic": 0.400000, "bitis": 0.600000, "saat": 8, "etiket": "Neutral (8h)"},
                    {"baslangic": 0.600000, "bitis": 1.000000, "saat": 4, "etiket": "Long Region (4h)"}
                ]
            }
        }
    }
    
    return coklu_senaryo_kaydet(default_senaryolar)