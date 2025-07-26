# main.py

import streamlit as st
import numpy as np
import pandas as pd
import json
import os
from datetime import datetime

# Yerel importlar
from config import HAZIR_MODLAR, VARSAYILAN_PARAMETRELER, ARAYUZ_AYARLARI, METINLER
from curve_functions import (
    cift_s_curve_sistemi_yeni, 
    sistem_istatistiklerini_hesapla_yeni,
    parametreleri_dogrula_yeni,
    gecis_bolgesi_bilgilerini_hesapla,
    duyarlilik_analizi_uret_yeni,
    cap_etkisi_analizi,
    belirli_pozisyondaki_funding_hesapla,
    funding_oran_hesaplamalari,
    funding_oran_hesaplamalari_dinamik,
    funding_bolgeleri_analizi
)
from visualization import (
    ana_grafigi_olustur_yeni,
    pozisyon_slider_widget,
    parametre_duyarlilik_grafigi_yeni,
    cap_etkisi_grafigi,
    istatistik_tablosu_olustur,
    funding_hesaplama_tablosu,
    gecis_bolgesi_detay_grafigi_yeni
)
from utils import (
    hazir_mod_yukle,
    kayitli_ayarlari_yukle,
    yeni_ayar_kaydet,
    ayar_sil,
    konfigurasyonu_dict_olarak_export_et,
    dict_ten_konfigurasyon_import_et,
    parametre_tablosu_olustur_yeni,
    funding_saatleri_tablosu_olustur,
    kritik_seviyeler_tablosu_olustur_yeni,
    json_dosyasi_dogrula,
    ozel_ayar_isimleri_listesi,
    varsayilan_ayarlari_yukle,
    # YENİ ÇOKLU SENARYO FONKSİYONLARI
    coklu_senaryo_yukle,
    coklu_senaryo_kaydet,
    yeni_senaryo_ekle,
    senaryo_sil,
    senaryo_isimleri_listesi,
    senaryo_yukle,
    json_dosyasi_dogrula_coklu,
    dict_ten_coklu_senaryo_import_et,
    settings_json_olustur_default
)

def session_state_baslat():
    """Session state başlangıç değerlerini ayarla ve settings.json'u otomatik yükle"""
    if 'mevcut_mod' not in st.session_state:
        st.session_state.mevcut_mod = 'Custom'
    
    if 'parametreler' not in st.session_state:
        # Önce settings.json'dan ayarları yüklemeyi dene
        settings_yuklendi = False
        
        try:
            # settings.json'da direkt parametreler var mı kontrol et (eski format)
            if os.path.exists("settings.json"):
                with open("settings.json", 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
                
                # Eski format - direkt parametreler varsa
                if 'parametreler' in settings_data and 'senaryolar' not in settings_data:
                    st.session_state.parametreler = settings_data['parametreler'].copy()
                    
                    # Funding bölgeleri de varsa ekle
                    if 'funding_bolgeleri' in settings_data:
                        st.session_state.parametreler['funding_bolgeleri'] = settings_data['funding_bolgeleri']
                    
                    # Kritik seviyeler de varsa ekle
                    if 'kritik_seviyeler' in settings_data:
                        st.session_state.parametreler['kritik_seviyeler'] = settings_data['kritik_seviyeler']
                    
                    settings_yuklendi = True
                    st.toast("✅ Settings.json'dan ayarlar yüklendi!", icon="⚙️")
                    
                # Yeni format - senaryolar varsa Default_Configuration'u yükle
                elif 'senaryolar' in settings_data:
                    senaryolar = settings_data['senaryolar']
                    
                    # Önce Default_Configuration'u ara
                    if 'Default_Configuration' in senaryolar:
                        default_config = senaryolar['Default_Configuration']
                        if 'parametreler' in default_config:
                            st.session_state.parametreler = default_config['parametreler'].copy()
                            settings_yuklendi = True
                            st.toast("✅ Default Configuration yüklendi!", icon="⚙️")
                    
                    # Default_Configuration yoksa ilk senaryoyu yükle
                    elif senaryolar:
                        ilk_senaryo_ismi = list(senaryolar.keys())[0]
                        ilk_senaryo = senaryolar[ilk_senaryo_ismi]
                        if 'parametreler' in ilk_senaryo:
                            st.session_state.parametreler = ilk_senaryo['parametreler'].copy()
                            st.session_state.mevcut_mod = ilk_senaryo_ismi
                            settings_yuklendi = True
                            st.toast(f"✅ '{ilk_senaryo_ismi}' senaryosu yüklendi!", icon="📋")
                
        except Exception as e:
            print(f"Settings.json yüklenirken hata: {e}")
            st.toast(f"⚠️ Settings.json yüklenemedi: {e}", icon="⚠️")
        
        # Eğer settings.json'dan yüklenemezse varsayılanları kullan
        if not settings_yuklendi:
            st.session_state.parametreler = varsayilan_ayarlari_yukle()
            st.toast("📝 Varsayılan ayarlar yüklendi", icon="📝")
    
    # Senaryoları session state'e yükle (her başlangıçta güncel tutmak için)
    if 'yuklu_senaryolar' not in st.session_state:
        try:
            senaryolar = coklu_senaryo_yukle()
            st.session_state.yuklu_senaryolar = senaryolar
            if senaryolar:
                st.toast(f"📚 {len(senaryolar)} senaryo yüklendi", icon="📚")
        except Exception as e:
            st.session_state.yuklu_senaryolar = {}
            print(f"Senaryolar yüklenirken hata: {e}")

def sidebar_olustur():
    """Sol sidebar'ı oluştur - üst kısımda ayar yönetimi"""
    
    # ==> EN ÜSTTE: AYAR YÖNETİMİ
    st.sidebar.header("🎛️ Senaryo Yönetimi")
    
    # Senaryo listesi
    senaryo_listesi = senaryo_isimleri_listesi()
    
    # Eğer settings.json yoksa oluştur
    if not senaryo_listesi:
        if st.sidebar.button("🚀 Default Senaryolar Oluştur"):
            settings_json_olustur_default()
            st.sidebar.success("Default senaryolar oluşturuldu!")
            st.rerun()
        st.sidebar.info("Henüz senaryo yok - default oluşturun")
        senaryo_listesi = ['Custom']
    else:
        senaryo_listesi = ['Custom'] + senaryo_listesi
    
    # Mevcut senaryo seçimi
    mevcut_senaryo = st.sidebar.selectbox(
        "📋 Senaryo Seç",
        senaryo_listesi,
        index=senaryo_listesi.index(st.session_state.mevcut_mod) if st.session_state.mevcut_mod in senaryo_listesi else 0
    )
    
    # Senaryo değiştiğinde parametreleri güncelle
    if mevcut_senaryo != st.session_state.mevcut_mod:
        st.session_state.mevcut_mod = mevcut_senaryo
        if mevcut_senaryo == 'Custom':
            st.session_state.parametreler = varsayilan_ayarlari_yukle()
        else:
            yeni_parametreler = senaryo_yukle(mevcut_senaryo)
            if yeni_parametreler:
                st.session_state.parametreler = yeni_parametreler
        st.rerun()
    
    # Hızlı İşlemler
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        # Hızlı Kaydet
        if st.button("💾 Hızlı Kaydet", key="hizli_kaydet_top"):
            if mevcut_senaryo != 'Custom':
                # Mevcut senaryoyu güncelle
                aciklama = f"Güncellenme: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                if yeni_senaryo_ekle(mevcut_senaryo, st.session_state.parametreler, aciklama):
                    st.sidebar.success("Güncellendi!")
            else:
                st.sidebar.error("Custom modda kaydetmek için isim gerekli!")
    
    with col2:
        # JSON Import
        json_dosya = st.file_uploader("📥 JSON", type=['json'], key="json_import_sidebar")
        
        if json_dosya is not None:
            try:
                json_data = json.loads(json_dosya.read())
                gecerli, mesaj = json_dosyasi_dogrula_coklu(json_data)
                
                if gecerli and st.button("⬆️ Yükle", key="json_yukle_sidebar"):
                    # Çoklu senaryo import
                    yeni_senaryolar = dict_ten_coklu_senaryo_import_et(json_data)
                    
                    # Mevcut senaryolarla birleştir
                    mevcut_senaryolar = coklu_senaryo_yukle()
                    mevcut_senaryolar.update(yeni_senaryolar)
                    
                    if coklu_senaryo_kaydet(mevcut_senaryolar):
                        st.sidebar.success(f"{len(yeni_senaryolar)} senaryo eklendi!")
                        st.rerun()
                elif not gecerli:
                    st.sidebar.error(f"❌ {mesaj}")
            except:
                st.sidebar.error("Geçersiz JSON!")
    
    # Yeni Senaryo Kaydet
    with st.sidebar.expander("➕ Yeni Senaryo Kaydet"):
        yeni_isim = st.text_input("Senaryo İsmi", key="yeni_senaryo_isim")
        yeni_aciklama = st.text_input("Açıklama (opsiyonel)", key="yeni_senaryo_aciklama")
        
        col_kaydet1, col_kaydet2 = st.columns(2)
        
        with col_kaydet1:
            if st.button("💾 Kaydet", key="yeni_senaryo_kaydet"):
                if yeni_isim.strip():
                    if yeni_senaryo_ekle(yeni_isim.strip(), st.session_state.parametreler, yeni_aciklama):
                        st.success("Kaydedildi!")
                        st.rerun()
                else:
                    st.error("İsim boş olamaz!")
        
        with col_kaydet2:
            # Settings.json'a Kaydet butonu
            if st.button("⚙️ Default Yap", key="senaryo_default_yap", help="Bu senaryoyu settings.json'a default olarak kaydet"):
                if yeni_isim.strip():
                    # Önce normal senaryo olarak kaydet
                    if yeni_senaryo_ekle(yeni_isim.strip(), st.session_state.parametreler, yeni_aciklama):
                        # Sonra settings.json'a da default olarak kaydet (eski formatla uyumlu)
                        settings_data = {
                            "sistem_versiyonu": "2.0",
                            "olusturulma_tarihi": datetime.now().isoformat(),
                            "parametreler": st.session_state.parametreler.copy(),
                            "funding_bolgeleri": st.session_state.parametreler.get('funding_bolgeleri', []),
                            "funding_saatleri": [1, 4, 8, 12, 24],
                            "kritik_seviyeler": {},
                            "metadata": {
                                "aciklama": f"Default Senaryo: {yeni_isim.strip()}",
                                "pozisyon_aciklama": "0.0 = Tam Short, 1.0 = Tam Long"
                            }
                        }
                        
                        try:
                            with open("settings.json", 'w', encoding='utf-8') as f:
                                json.dump(settings_data, f, indent=2, ensure_ascii=False)
                            st.success(f"✅ '{yeni_isim.strip()}' senaryo listesine ve settings.json'a kaydedildi!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Settings.json kaydetme hatası: {e}")
                else:
                    st.error("İsim boş olamaz!")
    
    # Senaryo Silme
    if mevcut_senaryo != 'Custom' and senaryo_listesi:
        with st.sidebar.expander("🗑️ Senaryo Sil"):
            if st.button(f"🗑️ '{mevcut_senaryo}' Senaryosunu Sil", key="senaryo_sil"):
                if senaryo_sil(mevcut_senaryo):
                    st.success("Silindi!")
                    st.session_state.mevcut_mod = 'Custom'
                    st.session_state.parametreler = varsayilan_ayarlari_yukle()
                    st.rerun()
    
    st.sidebar.markdown("---")
    
    # ==> PARAMETRELERİ GÖSTER/DÜZENLE
    st.sidebar.header("⚙️ Sistem Parametreleri")
    
    # Güvenlik kontrolü - eğer parametreler None ise varsayılanları yükle
    if st.session_state.parametreler is None:
        st.session_state.parametreler = varsayilan_ayarlari_yukle()
    
    # Short parametreleri
    st.sidebar.subheader("📉 Short Eğrisi")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        short_min_oran = st.number_input(
            "Min Oran",
            **ARAYUZ_AYARLARI['number_input_ayarlari']['oran'],
            value=st.session_state.parametreler.get('short_min_oran', -0.010000),
            key='short_min_oran'
        )
    
    with col2:
        short_max_oran = st.number_input(
            "Max Oran",
            **ARAYUZ_AYARLARI['number_input_ayarlari']['oran'],
            value=st.session_state.parametreler.get('short_max_oran', 0.000000),
            key='short_max_oran'
        )
    
    short_orta_nokta = st.sidebar.number_input(
        "Orta Nokta",
        **ARAYUZ_AYARLARI['number_input_ayarlari']['orta_nokta'],
        value=st.session_state.parametreler.get('short_orta_nokta', 0.200000),
        key='short_orta_nokta'
    )
    
    short_diklik = st.sidebar.number_input(
        "Diklik",
        **ARAYUZ_AYARLARI['number_input_ayarlari']['diklik'],
        value=st.session_state.parametreler.get('short_diklik', 2.000000),
        key='short_diklik'
    )
    
    st.sidebar.markdown("---")
    
    # Long parametreleri
    st.sidebar.subheader("📈 Long Eğrisi")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        long_min_oran = st.number_input(
            "Min Oran ",
            **ARAYUZ_AYARLARI['number_input_ayarlari']['oran'],
            value=st.session_state.parametreler.get('long_min_oran', 0.000000),
            key='long_min_oran'
        )
    
    with col2:
        long_max_oran = st.number_input(
            "Max Oran ",
            **ARAYUZ_AYARLARI['number_input_ayarlari']['oran'],
            value=st.session_state.parametreler.get('long_max_oran', 0.010000),
            key='long_max_oran'
        )
    
    long_orta_nokta = st.sidebar.number_input(
        "Orta Nokta ",
        **ARAYUZ_AYARLARI['number_input_ayarlari']['orta_nokta'],
        value=st.session_state.parametreler.get('long_orta_nokta', 0.800000),
        key='long_orta_nokta'
    )
    
    long_diklik = st.sidebar.number_input(
        "Diklik ",
        **ARAYUZ_AYARLARI['number_input_ayarlari']['diklik'],
        value=st.session_state.parametreler.get('long_diklik', 2.000000),
        key='long_diklik'
    )
    
    st.sidebar.markdown("---")
    
    # Sistem parametreleri
    st.sidebar.subheader("🔧 Sistem")
    
    gecis_genisligi = st.sidebar.number_input(
        "Geçiş Genişliği",
        **ARAYUZ_AYARLARI['number_input_ayarlari']['gecis_genisligi'],
        value=st.session_state.parametreler.get('gecis_genisligi', 0.050000),
        key='gecis_genisligi'
    )
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        min_cap = st.number_input(
            "Min Cap",
            **ARAYUZ_AYARLARI['number_input_ayarlari']['cap_deger'],
            value=st.session_state.parametreler.get('min_cap', -0.750000),
            key='min_cap'
        )
    
    with col2:
        max_cap = st.number_input(
            "Max Cap",
            **ARAYUZ_AYARLARI['number_input_ayarlari']['cap_deger'],
            value=st.session_state.parametreler.get('max_cap', 0.750000),
            key='max_cap'
        )
    
    st.sidebar.markdown("---")
    
    # Dinamik Funding Bölgeleri
    st.sidebar.subheader("⏱️ Dinamik Funding Bölgeleri")
    
    mevcut_bolgeler = st.session_state.parametreler.get('funding_bolgeleri', [
        {'baslangic': 0.000000, 'bitis': 0.200000, 'saat': 1, 'etiket': 'Ekstrem Short'},
        {'baslangic': 0.200000, 'bitis': 0.400000, 'saat': 2, 'etiket': 'Short'},
        {'baslangic': 0.400000, 'bitis': 0.600000, 'saat': 8, 'etiket': 'Normal'},
        {'baslangic': 0.600000, 'bitis': 0.800000, 'saat': 2, 'etiket': 'Long'},
        {'baslangic': 0.800000, 'bitis': 1.000000, 'saat': 1, 'etiket': 'Ekstrem Long'}
    ])
    
    bolge_sayisi = st.sidebar.number_input(
        "Bölge Sayısı",
        min_value=1,
        max_value=10,
        value=len(mevcut_bolgeler),
        step=1
    )
    
    funding_bolgeleri = []
    
    for i in range(bolge_sayisi):
        st.sidebar.markdown(f"**Bölge {i+1}**")
        
        col1, col2 = st.sidebar.columns(2)
        
        # Varsayılan değerler
        if i < len(mevcut_bolgeler):
            default_baslangic = mevcut_bolgeler[i]['baslangic']
            default_bitis = mevcut_bolgeler[i]['bitis'] 
            default_saat = mevcut_bolgeler[i]['saat']
            default_etiket = mevcut_bolgeler[i]['etiket']
        else:
            default_baslangic = i * (1.0 / bolge_sayisi)
            default_bitis = (i + 1) * (1.0 / bolge_sayisi)
            default_saat = 8
            default_etiket = f"Bölge {i+1}"
        
        with col1:
            baslangic = st.number_input(
                "Başlangıç",
                **ARAYUZ_AYARLARI['number_input_ayarlari']['orta_nokta'],
                value=default_baslangic,
                key=f'bolge_baslangic_{i}'
            )
        
        with col2:
            bitis = st.number_input(
                "Bitiş",
                **ARAYUZ_AYARLARI['number_input_ayarlari']['orta_nokta'],
                value=default_bitis,
                key=f'bolge_bitis_{i}'
            )
        
        col3, col4 = st.sidebar.columns(2)
        
        with col3:
            saat = st.number_input(
                "Saat",
                **ARAYUZ_AYARLARI['number_input_ayarlari']['saat'],
                value=default_saat,
                key=f'bolge_saat_{i}'
            )
        
        with col4:
            etiket = st.text_input(
                "Etiket",
                value=default_etiket,
                key=f'bolge_etiket_{i}'
            )
        
        funding_bolgeleri.append({
            'baslangic': baslangic,
            'bitis': bitis,
            'saat': saat,
            'etiket': etiket
        })
    
    # Parametreleri güncelle
    mevcut_parametreler = {
        'short_min_oran': short_min_oran,
        'short_max_oran': short_max_oran,
        'short_orta_nokta': short_orta_nokta,
        'short_diklik': short_diklik,
        'long_min_oran': long_min_oran,
        'long_max_oran': long_max_oran,
        'long_orta_nokta': long_orta_nokta,
        'long_diklik': long_diklik,
        'gecis_genisligi': gecis_genisligi,
        'min_cap': min_cap,
        'max_cap': max_cap,
        'funding_bolgeleri': funding_bolgeleri,
        'kritik_seviyeler': {}
    }
    
    return mevcut_parametreler

def ana_icerik_olustur(parametreler):
    """Ana içerik alanını oluştur"""
    
    # X değerlerini oluştur (0-1 arası) - sabit çözünürlük
    x_degerleri = np.linspace(0, 1, 500)
    
    # Eğrileri hesapla
    combined_curve, short_curve, long_curve = cift_s_curve_sistemi_yeni(
        x_degerleri,
        parametreler['short_min_oran'], parametreler['short_max_oran'],
        parametreler['short_orta_nokta'], parametreler['short_diklik'],
        parametreler['long_min_oran'], parametreler['long_max_oran'],
        parametreler['long_orta_nokta'], parametreler['long_diklik'],
        parametreler['gecis_genisligi'], parametreler['min_cap'], parametreler['max_cap']
    )
    
    # Geçiş bölgesi bilgilerini hesapla
    gecis_bilgileri = gecis_bolgesi_bilgilerini_hesapla(parametreler)
    
    # Ana grafik - dinamik funding bölgeleri ile
    st.subheader("Dinamik Funding Fee Sistemi")
    
    # DÜZELTME: Doğru parametreler geçiliyor
    ana_fig = ana_grafigi_olustur_yeni(
        x_degerleri, 
        combined_curve,
        parametreler.get('funding_bolgeleri'),  # funding_bolgeleri geçiliyor
        gecis_bilgileri['baslangic'], 
        gecis_bilgileri['bitis'],
        parametreler['min_cap'], 
        parametreler['max_cap']
    )
    
    st.plotly_chart(ana_fig, use_container_width=True)
    
    # Pozisyon slider widget - dinamik sıklık ile
    pozisyon, funding_orani, saat_dilimi = pozisyon_slider_widget(x_degerleri, combined_curve, parametreler)
    
    st.markdown("---")
    
    # İstatistikler
    istatistikler = sistem_istatistiklerini_hesapla_yeni(combined_curve)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📉 Min Oran", f"{istatistikler['min']:.6f}%")
    
    with col2:
        st.metric("📈 Max Oran", f"{istatistikler['max']:.6f}%")
    
    with col3:
        st.metric("📊 Ortalama", f"{istatistikler['ortalama']:.6f}%")
    
    with col4:
        st.metric("📏 Değer Aralığı", f"{istatistikler['aralik']:.6f}%")
    
    # Dinamik Funding Analizi
    st.subheader("⏱️ Dinamik Funding Bölgeleri Analizi")
    
    bolge_analizleri = funding_bolgeleri_analizi(parametreler.get('funding_bolgeleri', []), parametreler)
    
    if bolge_analizleri:
        bolge_df_data = []
        for analiz in bolge_analizleri:
            bolge = analiz['bolge']
            hesaplamalar = analiz['hesaplamalar']
            
            bolge_df_data.append({
                "🏷️ Bölge": bolge['etiket'],
                "📍 Pozisyon Aralığı": f"{bolge['baslangic']:.6f} - {bolge['bitis']:.6f}",
                "⏱️ Funding Sıklığı": f"{bolge['saat']} saat",
                "Günlük Kesim": f"{hesaplamalar['gunluk_kesim_sayisi']:.1f}x",
                "Orta Nokta Funding": f"{analiz['funding_orani']:.6f}%",
                "Günlük Toplam": f"{hesaplamalar['gunluk_oran']:.6f}%",
                "📈 Yıllık Toplam": f"{hesaplamalar['yillik_oran']:.3f}%"
            })
        
        bolge_df = pd.DataFrame(bolge_df_data)
        st.dataframe(bolge_df, use_container_width=True, hide_index=True)
    
    # Detaylı analiz sekmeleri
    tab1, tab2 = st.tabs([
        "📊 Sistem Detayları", 
        "Geçiş Bölgesi"
    ])
    
    with tab1:
        sistem_detaylarini_goster_yeni(x_degerleri, combined_curve, parametreler, istatistikler)
    
    with tab2:
        gecis_bolgesi_analizini_goster_yeni(x_degerleri, combined_curve, gecis_bilgileri, parametreler)

def sistem_detaylarini_goster_yeni(x_degerleri, combined_curve, parametreler, istatistikler):
    """Sistem detayları sekmesi"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sistem İstatistikleri")
        
        # İstatistik tablosu
        istatistik_df = istatistik_tablosu_olustur(istatistikler)
        st.dataframe(istatistik_df, use_container_width=True, hide_index=True)
        
        st.subheader("Funding Saat Dilimleri")
        
        # Dinamik funding bölgelerinden saatleri al
        funding_bolgeleri = parametreler.get('funding_bolgeleri', [])
        saat_dilimleri = []
        for bolge in funding_bolgeleri:
            if bolge['saat'] not in saat_dilimleri:
                saat_dilimleri.append(bolge['saat'])
        
        if not saat_dilimleri:
            saat_dilimleri = [8]  # Default
        
        # Funding saatleri tablosu
        funding_saat_df = funding_saatleri_tablosu_olustur(saat_dilimleri)
        st.dataframe(funding_saat_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("⚙️ Parametre Özeti")
        
        # Parametre tablosu
        parametre_df = parametre_tablosu_olustur_yeni(parametreler)
        st.dataframe(parametre_df, use_container_width=True, hide_index=True)
        
        # Kritik seviyeler
        if parametreler.get('kritik_seviyeler'):
            st.subheader("📍 Kritik Seviyeler")
            kritik_df = kritik_seviyeler_tablosu_olustur_yeni(parametreler['kritik_seviyeler'])
            st.dataframe(kritik_df, use_container_width=True, hide_index=True)
    
    # Funding hesaplama tablosu
    st.subheader("Farklı Saat Dilimlerinde Funding Hesaplaması")
    st.caption("0.5 pozisyonundaki (nötr) funding oranı baz alınarak hesaplanmıştır")
    
    # 0.5 pozisyonundaki funding'i hesapla
    notr_funding, _ = belirli_pozisyondaki_funding_hesapla(0.5, parametreler)
    
    funding_hesap_df = funding_hesaplama_tablosu(notr_funding, saat_dilimleri)
    st.dataframe(funding_hesap_df, use_container_width=True, hide_index=True)

def parametre_analizini_goster_yeni(x_degerleri, parametreler):
    """Parametre analizi sekmesi"""
    
    st.subheader("🔍 Parametre Duyarlılık Analizi")
    
    # Parametre seçimi
    parametre_secenekleri = {
        'short_diklik': 'Short Eğri Dikliği',
        'long_diklik': 'Long Eğri Dikliği', 
        'gecis_genisligi': 'Geçiş Genişliği',
        'short_min_oran': 'Short Min Oran',
        'short_max_oran': 'Short Max Oran',
        'long_min_oran': 'Long Min Oran',
        'long_max_oran': 'Long Max Oran'
    }
    
    secilen_parametre = st.selectbox(
        "Analiz için Parametre Seçin",
        options=list(parametre_secenekleri.keys()),
        format_func=lambda x: parametre_secenekleri[x]
    )
    
    # Varyasyon aralığı
    mevcut_deger = parametreler[secilen_parametre]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        varyasyon_min = st.number_input("Min Değer", value=max(0.0, mevcut_deger - 1.0), step=0.1)
    with col2:
        varyasyon_max = st.number_input("Max Değer", value=mevcut_deger + 1.0, step=0.1)
    with col3:
        varyasyon_adim = st.number_input("Adım Sayısı", min_value=3, max_value=7, value=5, step=1)
    
    varyasyon_araligi = np.linspace(varyasyon_min, varyasyon_max, varyasyon_adim)
    
    # Duyarlılık analizi
    duyarlilik_verileri = duyarlilik_analizi_uret_yeni(parametreler, secilen_parametre, varyasyon_araligi, x_degerleri)
    
    # Temel eğri için
    temel_curve, _, _ = cift_s_curve_sistemi_yeni(
        x_degerleri,
        parametreler['short_min_oran'], parametreler['short_max_oran'],
        parametreler['short_orta_nokta'], parametreler['short_diklik'],
        parametreler['long_min_oran'], parametreler['long_max_oran'],
        parametreler['long_orta_nokta'], parametreler['long_diklik'],
        parametreler['gecis_genisligi'], parametreler['min_cap'], parametreler['max_cap']
    )
    
    # Duyarlılık grafiği
    duyarlilik_fig = parametre_duyarlilik_grafigi_yeni(
        x_degerleri, temel_curve, duyarlilik_verileri, parametre_secenekleri[secilen_parametre]
    )
    
    st.plotly_chart(duyarlilik_fig, use_container_width=True)
    
    # Etki özeti
    st.subheader("📊 Parametre Etki Özeti")
    
    etki_verileri = []
    for var_degeri, funding_degerleri in duyarlilik_verileri.items():
        etki_verileri.append({
            "Parametre Değeri": f"{var_degeri:.3f}",
            "Min Oran": f"{funding_degerleri.min():.4f}%",
            "Max Oran": f"{funding_degerleri.max():.4f}%",
            "Ortalama": f"{funding_degerleri.mean():.4f}%",
            "Aralık": f"{funding_degerleri.max() - funding_degerleri.min():.4f}%"
        })
    
    etki_df = pd.DataFrame(etki_verileri)
    st.dataframe(etki_df, use_container_width=True, hide_index=True)

def gecis_bolgesi_analizini_goster_yeni(x_degerleri, combined_curve, gecis_bilgileri, parametreler):
    """Geçiş bölgesi analizi sekmesi"""
    
    st.subheader("Geçiş Bölgesi Detaylı Analizi")
    
    # Geçiş görselleştirmesi
    gecis_fig = gecis_bolgesi_detay_grafigi_yeni(x_degerleri, combined_curve, gecis_bilgileri)
    st.plotly_chart(gecis_fig, use_container_width=True)
    
    # Geçiş bölgesi istatistikleri
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Geçiş Bölgesi Bilgileri")
        
        gecis_info_df = pd.DataFrame([
            {"Özellik": "Merkez Pozisyonu", "Değer": f"{gecis_bilgileri['merkez']:.3f}"},
            {"Özellik": "Başlangıç Pozisyonu", "Değer": f"{gecis_bilgileri['baslangic']:.3f}"},
            {"Özellik": "Bitiş Pozisyonu", "Değer": f"{gecis_bilgileri['bitis']:.3f}"},
            {"Özellik": "Toplam Genişlik", "Değer": f"{gecis_bilgileri['genislik']:.3f}"},
            {"Özellik": "Toplam Pozisyonun %'si", "Değer": f"{gecis_bilgileri['genislik'] * 100:.1f}%"}
        ])
        
        st.dataframe(gecis_info_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("⚙️ Geçiş Kalitesi")
        
        # Geçiş bölgesindeki funding analizi
        gecis_maskesi = ((x_degerleri >= gecis_bilgileri['baslangic']) & 
                        (x_degerleri <= gecis_bilgileri['bitis']))
        
        if np.any(gecis_maskesi):
            gecis_funding = combined_curve[gecis_maskesi]
            
            gecis_kalite_df = pd.DataFrame([
                {"Metrik": "Geçiş Bölgesi Min", "Değer": f"{gecis_funding.min():.4f}%"},
                {"Metrik": "Geçiş Bölgesi Max", "Değer": f"{gecis_funding.max():.4f}%"},
                {"Metrik": "Geçiş Değer Aralığı", "Değer": f"{gecis_funding.max() - gecis_funding.min():.4f}%"},
                {"Metrik": "Geçiş Nokta Sayısı", "Değer": f"{len(gecis_funding)}"},
                {"Metrik": "Pürüzsüzlük Skoru", "Değer": f"{1 / (1 + np.std(np.gradient(gecis_funding))):.3f}"}
            ])
            
            st.dataframe(gecis_kalite_df, use_container_width=True, hide_index=True)

def cap_analizini_goster(x_degerleri, parametreler):
    """Cap analizi sekmesi"""
    
    st.subheader("⚠️ Cap Değerlerinin Etkisi")
    
    # Cap etkisi analizi
    cap_analizi = cap_etkisi_analizi(x_degerleri, parametreler, parametreler['min_cap'], parametreler['max_cap'])
    
    # Cap etkisi grafiği
    cap_fig = cap_etkisi_grafigi(
        x_degerleri, 
        cap_analizi['orijinal_curve'], 
        cap_analizi['capli_curve'],
        parametreler['min_cap'], 
        parametreler['max_cap']
    )
    
    st.plotly_chart(cap_fig, use_container_width=True)
    
    # Cap istatistikleri
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Cap Etki İstatistikleri")
        
        cap_istatistik_df = pd.DataFrame([
            {"Metrik": "Min Cap'te Kesilen Nokta", "Değer": f"{cap_analizi['min_kesilen_nokta']}"},
            {"Metrik": "Max Cap'te Kesilen Nokta", "Değer": f"{cap_analizi['max_kesilen_nokta']}"},
            {"Metrik": "Toplam Kesilen Nokta", "Değer": f"{cap_analizi['toplam_kesilen']}"},
            {"Metrik": "Toplam Nokta Sayısı", "Değer": f"{cap_analizi['toplam_nokta']}"},
            {"Metrik": "Kesinti Oranı", "Değer": f"{cap_analizi['toplam_kesilen'] / cap_analizi['toplam_nokta'] * 100:.1f}%"}
        ])
        
        st.dataframe(cap_istatistik_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("⚙️ Cap Önerileri")
        
        orijinal_min = cap_analizi['orijinal_curve'].min()
        orijinal_max = cap_analizi['orijinal_curve'].max()
        
        cap_oneri_df = pd.DataFrame([
            {"Öneri": "Mevcut Min Cap", "Değer": f"{parametreler['min_cap']:.3f}%"},
            {"Öneri": "Mevcut Max Cap", "Değer": f"{parametreler['max_cap']:.3f}%"},
            {"Öneri": "Önerilen Min Cap", "Değer": f"{orijinal_min:.3f}%"},
            {"Öneri": "Önerilen Max Cap", "Değer": f"{orijinal_max:.3f}%"},
            {"Öneri": "Güvenli Min Cap", "Değer": f"{orijinal_min * 1.1:.3f}%"},
            {"Öneri": "Güvenli Max Cap", "Değer": f"{orijinal_max * 1.1:.3f}%"}
        ])
        
        st.dataframe(cap_oneri_df, use_container_width=True, hide_index=True)
        
        if cap_analizi['toplam_kesilen'] > 0:
            st.warning(f"⚠️ {cap_analizi['toplam_kesilen']} nokta cap tarafından kesiliyor!")
        else:
            st.success("✅ Cap değerleri etkili değil - tüm eğri korunuyor")

def export_import_goster_yeni(parametreler, x_degerleri, combined_curve):
    """Export/Import sekmesi"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 Export İşlemleri")
        
        # JSON export
        konfig_dict = konfigurasyonu_dict_olarak_export_et(parametreler)
        konfig_json = json.dumps(konfig_dict, indent=2, ensure_ascii=False)
        
        st.download_button(
            label="🗂️ Konfigürasyonu JSON olarak İndir",
            data=konfig_json,
            file_name=f"funding_konfig_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
        # CSV export
        sonuc_df = pd.DataFrame({
            'Pozisyon': x_degerleri,
            'Funding_Orani': combined_curve
        })
        
        csv_verisi = sonuc_df.to_csv(index=False)
        
        st.download_button(
            label="📊 Sonuçları CSV olarak İndir",
            data=csv_verisi,
            file_name=f"funding_sonuclari_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Konfigürasyon önizleme
        with st.expander("📋 Konfigürasyon Önizleme"):
            st.code(konfig_json, language='json', line_numbers=True)
    
    with col2:
        st.subheader("📥 Import İşlemleri")
        
        # JSON dosya yükleme
        yuklenen_dosya = st.file_uploader(
            "📁 JSON Konfigürasyon Dosyası Yükle",
            type=['json'],
            help="Daha önce export edilmiş konfigürasyon dosyası yükleyin"
        )
        
        if yuklenen_dosya is not None:
            try:
                konfig_verisi = json.loads(yuklenen_dosya.read())
                
                # JSON doğrulama
                gecerli, mesaj = json_dosyasi_dogrula(konfig_verisi)
                
                if gecerli:
                    st.success(f"✅ Geçerli dosya: {mesaj}")
                    
                    if st.button("🚀 Konfigürasyonu Yükle", key="konfig_yukle"):
                        try:
                            yeni_parametreler = dict_ten_konfigurasyon_import_et(konfig_verisi)
                            
                            # Parametre doğrulama
                            hatalar = parametreleri_dogrula_yeni(yeni_parametreler)
                            
                            if hatalar:
                                st.error("❌ Konfigürasyon doğrulama başarısız:")
                                for hata in hatalar:
                                    st.error(f"- {hata}")
                            else:
                                # Session state'i güncelle
                                st.session_state.parametreler = yeni_parametreler
                                st.session_state.mevcut_mod = 'Özel'
                                st.success("🎉 Konfigürasyon başarıyla yüklendi!")
                                st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Yükleme hatası: {str(e)}")
                    
                    # Yüklenen konfigürasyon önizlemesi
                    with st.expander("👁️ Yüklenen Konfigürasyon Önizleme"):
                        st.json(konfig_verisi)
                
                else:
                    st.error(f"❌ {mesaj}")
                    
            except json.JSONDecodeError:
                st.error("❌ Geçersiz JSON dosyası. Lütfen geçerli bir konfigürasyon dosyası yükleyin.")
            except Exception as e:
                st.error(f"❌ Dosya okuma hatası: {str(e)}")
        
        # Hızlı reset
        st.markdown("---")
        st.subheader("Hızlı İşlemler")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🏠 Varsayılan Ayarlara Dön", key="varsayilan_don"):
                st.session_state.parametreler = varsayilan_ayarlari_yukle()
                st.session_state.mevcut_mod = 'Özel'
                st.success("Varsayılan ayarlar yüklendi!")
                st.rerun()
        
        with col_b:
            if st.button("📋 Mevcut Ayarları Kopyala", key="ayar_kopyala"):
                st.session_state['kopyalanan_ayarlar'] = st.session_state.parametreler.copy()
                st.success("📄 Ayarlar panoya kopyalandı!")

def main():
    """Ana uygulama fonksiyonu"""
    
    # Sayfa konfigürasyonu
    st.set_page_config(
        page_title="Funding Fee Sistemi v2.0",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Session state başlat
    session_state_baslat()
    
    # JSON İşlemleri - EN ÜSTTE (Settings.json yönetimi eklendi)
    st.header("🎛️ Hızlı JSON İşlemleri")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON Export
        st.subheader("📤 Export")
        if st.button("📁 JSON Export", key="json_export_top", use_container_width=True):
            konfig_dict = konfigurasyonu_dict_olarak_export_et(st.session_state.parametreler)
            konfig_json = json.dumps(konfig_dict, indent=2, ensure_ascii=False)
            
            st.download_button(
                label="⬇️ Dosyayı İndir",
                data=konfig_json,
                file_name=f"funding_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="json_download_top",
                use_container_width=True
            )
    
    with col2:
        # JSON Import
        st.subheader("📥 Import")
        yuklenen_dosya = st.file_uploader(
            "JSON Dosya Seç",
            type=['json'],
            key="json_upload_top",
            help="Daha önce export edilmiş ayar dosyası yükleyin"
        )
        
        if yuklenen_dosya is not None:
            try:
                konfig_verisi = json.loads(yuklenen_dosya.read())
                gecerli, mesaj = json_dosyasi_dogrula(konfig_verisi)
                
                if gecerli and st.button("⬆️ Ayarları Yükle", key="json_load_top", use_container_width=True):
                    yeni_parametreler = dict_ten_konfigurasyon_import_et(konfig_verisi)
                    st.session_state.parametreler = yeni_parametreler
                    st.session_state.mevcut_mod = 'Custom'
                    st.success("✅ Ayarlar başarıyla yüklendi!")
                    st.rerun()
                elif not gecerli:
                    st.error(f"❌ {mesaj}")
            except:
                st.error("❌ Geçersiz JSON dosyası!")
    
    with col3:
        # Settings.json Yönetimi
        st.subheader("⚙️ Settings.json")
        
        # Settings.json İndir
        if st.button("📥 Settings.json İndir", key="settings_download", use_container_width=True):
            try:
                settings_data = coklu_senaryo_yukle()
                if settings_data:
                    # Tam settings.json formatında export et
                    full_settings = {
                        "sistem_versiyonu": "2.0",
                        "olusturulma_tarihi": datetime.now().isoformat(),
                        "senaryolar": settings_data,
                        "metadata": {
                            "aciklama": "Funding Fee Sistemi Senaryolar",
                            "senaryo_sayisi": len(settings_data),
                            "son_guncelleme": datetime.now().strftime('%Y-%m-%d'),
                            "kullanim": "Senaryo ismi ile doğrudan yüklenebilir"
                        }
                    }
                    settings_json = json.dumps(full_settings, indent=2, ensure_ascii=False)
                    
                    st.download_button(
                        label="⬇️ Settings.json İndir",
                        data=settings_json,
                        file_name=f"settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        key="settings_json_download",
                        use_container_width=True
                    )
                else:
                    st.error("Settings.json bulunamadı!")
            except Exception as e:
                st.error(f"Settings.json indirilemedi: {e}")
        
        # Default Settings.json Kaydet
        if st.button("💾 Default Olarak Kaydet", key="save_as_default", use_container_width=True):
            try:
                # Mevcut parametreleri default olarak settings.json'a kaydet
                default_senaryo = {
                    "Default_Configuration": {
                        "isim": "Default Configuration",
                        "aciklama": f"Default olarak kaydedildi - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                        "kayit_tarihi": datetime.now().isoformat(),
                        "parametreler": st.session_state.parametreler.copy()
                    }
                }
                
                # Mevcut senaryolarla birleştir
                mevcut_senaryolar = coklu_senaryo_yukle()
                mevcut_senaryolar.update(default_senaryo)
                
                if coklu_senaryo_kaydet(mevcut_senaryolar):
                    st.success("✅ Default configuration kaydedildi!")
                else:
                    st.error("❌ Kaydetme başarısız!")
            except Exception as e:
                st.error(f"❌ Hata: {e}")
        
        # Settings.json Değiştir
        settings_dosya = st.file_uploader(
            "Settings.json Değiştir",
            type=['json'],
            key="settings_replace",
            help="Yeni settings.json yükleyip mevcut olanı değiştirin"
        )
        
        if settings_dosya is not None:
            try:
                settings_verisi = json.loads(settings_dosya.read())
                if st.button("🔄 Settings.json Değiştir", key="replace_settings", use_container_width=True):
                    # Settings.json formatını kontrol et
                    if 'senaryolar' in settings_verisi:
                        if coklu_senaryo_kaydet(settings_verisi['senaryolar']):
                            st.success("✅ Settings.json başarıyla değiştirildi!")
                            st.rerun()
                        else:
                            st.error("❌ Settings.json kaydedilemedi!")
                    else:
                        st.error("❌ Geçersiz settings.json formatı!")
            except:
                st.error("❌ Geçersiz JSON dosyası!")
    
    st.markdown("---")
    
    # Ana başlık
    st.title("Borsa Funding Fee Sistemi")
    st.markdown("**⚡ Dinamik funding sıklığı - Ekstrem pozisyonlarda yüksek sıklık**")
    st.caption("🔴 0.000000 = Tam Short | 🟡 0.500000 = Nötr | 🟢 1.000000 = Tam Long")
    st.markdown("---")
    
    # Sidebar parametreleri
    parametreler = sidebar_olustur()
    
    # Parametreleri session state'e kaydet
    st.session_state.parametreler = parametreler
    
    # Parametre doğrulama
    dogrulama_hatalari = parametreleri_dogrula_yeni(parametreler)
    if dogrulama_hatalari:
        st.error("❌ Parametre doğrulama hataları:")
        for hata in dogrulama_hatalari:
            st.error(f"- {hata}")
        return
    
    # Ana içerik
    ana_icerik_olustur(parametreler)
    
    # Footer
    st.markdown("---")
    st.markdown("**🚀 Dinamik Funding Fee Sistemi v2.0** - Ekstrem pozisyonlarda yüksek sıklık")
    st.caption("💡 Geçiş genişliği: 0.05 | JSON import/export üstte | Pozisyona göre dinamik sıklık | Gelişmiş grafik tasarımı")


if __name__ == "__main__":
    main()