# config.py

VARSAYILAN_PARAMETRELER = {
    'gecis_genisligi': 0.050000,
    'min_cap': -0.750000,
    'max_cap': 0.750000
}

HAZIR_MODLAR = {
    'Custom': {
        'isim': 'Custom Settings',
        'short_min_oran': -0.010000,
        'short_max_oran': 0.000000,
        'short_orta_nokta': 0.200000,
        'short_diklik': 2.000000,
        'long_min_oran': 0.000000,
        'long_max_oran': 0.010000,
        'long_orta_nokta': 0.800000,
        'long_diklik': 2.000000,
        'gecis_genisligi': 0.050000,
        'min_cap': -0.750000,
        'max_cap': 0.750000,
        'funding_bolgeleri': [
            {'baslangic': 0.000000, 'bitis': 0.200000, 'saat': 1, 'etiket': 'Ekstrem Short'},
            {'baslangic': 0.200000, 'bitis': 0.400000, 'saat': 2, 'etiket': 'Short'},
            {'baslangic': 0.400000, 'bitis': 0.600000, 'saat': 8, 'etiket': 'Normal'},
            {'baslangic': 0.600000, 'bitis': 0.800000, 'saat': 2, 'etiket': 'Long'},
            {'baslangic': 0.800000, 'bitis': 1.000000, 'saat': 1, 'etiket': 'Ekstrem Long'}
        ],
        'kritik_seviyeler': {}
    }
}

BINANCE_DEFAULT = {
    'sistem_versiyonu': '2.0',
    'olusturulma_tarihi': '2025-01-01T00:00:00',
    'parametreler': {
        'short_min_oran': -0.010000,
        'short_max_oran': 0.000000,
        'short_orta_nokta': 0.200000,
        'short_diklik': 2.500000,
        'long_min_oran': 0.000000,
        'long_max_oran': 0.010000,
        'long_orta_nokta': 0.800000,
        'long_diklik': 2.500000,
        'gecis_genisligi': 0.050000,
        'min_cap': -0.750000,
        'max_cap': 0.750000
    },
    'funding_bolgeleri': [
        {'baslangic': 0.000000, 'bitis': 0.100000, 'saat': 1, 'etiket': 'Ekstrem Short (1h)'},
        {'baslangic': 0.100000, 'bitis': 0.300000, 'saat': 2, 'etiket': 'Yüksek Short (2h)'},
        {'baslangic': 0.300000, 'bitis': 0.450000, 'saat': 4, 'etiket': 'Orta Short (4h)'},
        {'baslangic': 0.450000, 'bitis': 0.550000, 'saat': 8, 'etiket': 'Normal (8h)'},
        {'baslangic': 0.550000, 'bitis': 0.700000, 'saat': 4, 'etiket': 'Orta Long (4h)'},
        {'baslangic': 0.700000, 'bitis': 0.900000, 'saat': 2, 'etiket': 'Yüksek Long (2h)'},
        {'baslangic': 0.900000, 'bitis': 1.000000, 'saat': 1, 'etiket': 'Ekstrem Long (1h)'}
    ],
    'kritik_seviyeler': {},
    'metadata': {
        'aciklama': 'Binance-style Dynamic Funding Fee System',
        'pozisyon_aciklama': '0.0 = Full Short, 1.0 = Full Long',
        'funding_logic': 'Extreme positions = higher frequency',
        'normal_range': '±0.01%',
        'extreme_cap': '±0.75%'
    }
}

ARAYUZ_AYARLARI = {
    'sidebar_genisligi': 350,
    'ana_grafik_yuksekligi': 600,
    'istatistik_yuksekligi': 300,
    'number_input_ayarlari': {
        'oran': {'min_value': -10.000000, 'max_value': 10.000000, 'step': 0.000001, 'format': "%.6f"},
        'orta_nokta': {'min_value': 0.000000, 'max_value': 1.000000, 'step': 0.000001, 'format': "%.6f"},
        'diklik': {'min_value': 0.000000, 'max_value': 50.000000, 'step': 0.000001, 'format': "%.6f"},
        'gecis_genisligi': {'min_value': 0.000001, 'max_value': 0.999999, 'step': 0.000001, 'format': "%.6f"},
        'cap_deger': {'min_value': -10.000000, 'max_value': 10.000000, 'step': 0.000001, 'format': "%.6f"},
        'saat': {'min_value': 1, 'max_value': 168, 'step': 1, 'format': "%d"}
    }
}

RENKLER = {
    'short_curve': '#dc3545',      
    'long_curve': '#28a745',       
    'combined_curve': '#007bff',   
    'transition': '#ffc107',       
    'neutral': '#6c757d',          
    'background': '#f8f9fa',       
    'zero_line': '#000000',        
    'cap_lines': '#ff6b6b'         
}

METINLER = {
    'baslik': 'Borsa Funding Fee Ayarlama Sistemi',
    'aciklama': 'Binance-style funding fee sistemi',
    'short_bolge': 'Short Bölgesi',
    'long_bolge': 'Long Bölgesi',
    'gecis_bolgesi': 'Geçiş Bölgesi',
    'funding_orani': 'Funding Oranı (%)',
    'pozisyon_orani': 'Pozisyon Oranı (0=Tam Short, 1=Tam Long)',
    'min_oran': 'Min Oran',
    'max_oran': 'Max Oran',
    'ortalama': 'Ortalama',
    'volatilite': 'Volatilite',
    'gunluk_oran': 'Günlük Oran',
    'yillik_oran': 'Yıllık Oran',
    'saatlik_oran': 'Saatlik Oran'
}

AYAR_DOSYA_YOLU = "kayitli_ayarlar.json"