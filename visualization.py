# visualization.py

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import streamlit as st
from config import RENKLER, METINLER

def ana_grafigi_olustur_yeni(x_degerleri, combined_curve, 
                            funding_bolgeleri=None, gecis_baslangic=None, gecis_bitis=None,
                            min_cap=None, max_cap=None):

    fig = go.Figure()
    
    if funding_bolgeleri:
        renk_mapping = {
            'ekstrem_short': {'color': '#FFE5E5', 'border': '#E74C3C', 'text_color': '#C0392B'},
            'yuksek_short': {'color': '#FFEBE0', 'border': '#E67E22', 'text_color': '#D35400'},
            'orta_short': {'color': '#FFF5E6', 'border': '#F39C12', 'text_color': '#E67E22'},
            'normal': {'color': '#E8F6F3', 'border': '#1ABC9C', 'text_color': '#16A085'},
            'orta_long': {'color': '#E8F8F5', 'border': '#27AE60', 'text_color': '#229954'},
            'yuksek_long': {'color': '#E5F5E9', 'border': '#28B463', 'text_color': '#1E8449'},
            'ekstrem_long': {'color': '#E8F5E8', 'border': '#58D68D', 'text_color': '#239B56'}
        }
        
        def bolge_tipini_belirle(etiket, saat):
            etiket_lower = etiket.lower()
            if 'ekstrem' in etiket_lower and 'short' in etiket_lower:
                return 'ekstrem_short'
            elif ('yüksek' in etiket_lower or 'high' in etiket_lower) and 'short' in etiket_lower:
                return 'yuksek_short'
            elif 'orta' in etiket_lower and 'short' in etiket_lower:
                return 'orta_short'
            elif 'normal' in etiket_lower or saat >= 6:
                return 'normal'
            elif 'orta' in etiket_lower and 'long' in etiket_lower:
                return 'orta_long'
            elif ('yüksek' in etiket_lower or 'high' in etiket_lower) and 'long' in etiket_lower:
                return 'yuksek_long'
            elif 'ekstrem' in etiket_lower and 'long' in etiket_lower:
                return 'ekstrem_long'
            else:
                return 'normal'
        
        for bolge in funding_bolgeleri:
            bolge_tipi = bolge_tipini_belirle(bolge['etiket'], bolge['saat'])
            renk_info = renk_mapping.get(bolge_tipi, renk_mapping['normal'])
            
            # Bölge arka plan rengi
            fig.add_vrect(
                x0=bolge['baslangic'], 
                x1=bolge['bitis'],
                fillcolor=renk_info['color'],
                opacity=0.6,
                layer="below",
                line_width=2,
                line_color=renk_info['border'],
                annotation_text=f"<b>{bolge['etiket']}</b><br>{bolge['saat']}h sıklık",
                annotation_position="top left",
                annotation=dict(
                    font=dict(size=11, color=renk_info['text_color']),
                    bgcolor="rgba(255,255,255,0.9)",
                    bordercolor=renk_info['border'],
                    borderwidth=1,
                    borderpad=4
                )
            )
    
    fig.add_trace(
        go.Scatter(
            x=x_degerleri,
            y=combined_curve,
            mode='lines',
            name='Funding Oranı',
            line=dict(
                color='#00D2FF', 
                width=5,
                shape='spline'  # Daha pürüzsüz eğri
            ),
            fill='tozeroy',  # Sıfır çizgisine kadar doldur
            fillcolor='rgba(0, 210, 255, 0.15)',
            hovertemplate='<b>📍 Pozisyon:</b> %{x:.6f}<br><b>Funding:</b> %{y:.6f}%<extra></extra>'
        )
    )
    
    if gecis_baslangic is not None and gecis_bitis is not None:
        fig.add_vrect(
            x0=gecis_baslangic, x1=gecis_bitis,
            fillcolor='rgba(241, 196, 15, 0.3)',
            line_color='#F1C40F',
            line_width=2,
            layer="below",
            annotation_text="Geçiş Bölgesi",
            annotation_position="top right",
            annotation=dict(
                font=dict(size=12, color='#F39C12'),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#F39C12",
                borderwidth=1
            )
        )
    
    if min_cap is not None:
        fig.add_hline(
            y=min_cap,
            line_dash="dash",
            line_color='#E74C3C',
            line_width=3,
            opacity=0.8,
            annotation_text=f"🔻 Min Cap: {min_cap:.3f}%",
            annotation_position="left",
            annotation=dict(
                font=dict(color='#E74C3C', size=12),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#E74C3C",
                borderwidth=1
            )
        )
    
    if max_cap is not None:
        fig.add_hline(
            y=max_cap,
            line_dash="dash",
            line_color='#E74C3C',
            line_width=3,
            opacity=0.8,
            annotation_text=f"🔺 Max Cap: {max_cap:.3f}%",
            annotation_position="left",
            annotation=dict(
                font=dict(color='#E74C3C', size=12),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#E74C3C",
                borderwidth=1
            )
        )
    
    fig.add_hline(
        y=0, 
        line_color='white', 
        line_width=4, 
        opacity=0.9,
        annotation_text="⚖️ Nötr Çizgi",
        annotation_position="right",
        annotation=dict(
            font=dict(color='white', size=12),
            bgcolor="rgba(255,255,255,0.1)"
        )
    )
    
    fig.add_vline(
        x=0.5, 
        line_color='white', 
        line_width=3, 
        line_dash="dot",
        opacity=0.7,
        annotation_text="Nötr Pozisyon",
        annotation_position="bottom",
        annotation=dict(
            font=dict(color='white', size=12),
            bgcolor="rgba(255,255,255,0.1)"
        )
    )
    

    fig.update_layout(
        title=dict(
            text="<b>Dinamik Funding Fee Sistemi</b><br><sub>Pozisyona Göre Değişken Sıklık - Ekstrem Pozisyonlarda Yüksek Sıklık</sub>",
            x=0.5,
            font=dict(size=22, color='white', family="Arial"),
            pad=dict(t=20)
        ),
        xaxis_title="<b>Pozisyon Oranı</b> (0=Tam Short, 1=Tam Long)",
        yaxis_title="<b>Funding Oranı (%)</b>",
        height=650,
        template="plotly_dark",
        hovermode='x unified',
        showlegend=False,
        paper_bgcolor='#1a1a1a',
        plot_bgcolor='#2d2d2d',
        margin=dict(t=100, b=80, l=80, r=80),
        font=dict(family="Arial", size=12, color='white')
    )
    
    fig.update_xaxes(
        range=[0, 1], 
        tickformat='.3f',
        gridcolor='rgba(255,255,255,0.3)',
        gridwidth=1,
        tickfont=dict(size=14, color='white'),
        title_font=dict(size=16, color='white'),
        showspikes=True,
        spikethickness=2,
        spikecolor="white",
        spikemode="across"
    )
    
    if len(combined_curve) > 0:
        y_min = combined_curve.min()
        y_max = combined_curve.max()
        y_range = y_max - y_min
        padding = y_range * 0.15 if y_range > 0 else 0.001
        fig.update_yaxes(
            range=[y_min - padding, y_max + padding],
            tickformat='.4f',
            gridcolor='rgba(255,255,255,0.3)',
            gridwidth=1,
            tickfont=dict(size=14, color='white'),
            title_font=dict(size=16, color='white'),
            showspikes=True,
            spikethickness=2,
            spikecolor="white",
            spikemode="across"
        )
    
    return fig

def pozisyon_slider_widget(x_degerleri, combined_curve, parametreler):

    st.subheader("Anlık Pozisyon Analizi - Dinamik Funding")
    
    pozisyon = st.slider(
        "Market Pozisyon Oranı",
        min_value=0.000000,
        max_value=1.000000,
        value=0.500000,
        step=0.000001,
        format="%.6f",
        help="0.000000 = Tam Short, 1.000000 = Tam Long"
    )
    
    from curve_functions import belirli_pozisyondaki_funding_hesapla, funding_oran_hesaplamalari_dinamik
    
    try:
        funding_orani, saat_dilimi = belirli_pozisyondaki_funding_hesapla(pozisyon, parametreler)
        
        if isinstance(funding_orani, (list, tuple, np.ndarray)):
            funding_orani = float(funding_orani[0]) if len(funding_orani) > 0 else 0.0
        else:
            funding_orani = float(funding_orani)
            
        saat_dilimi = int(saat_dilimi)
        
    except Exception as e:
        st.error(f"Funding hesaplama hatası: {e}")
        funding_orani = 0.0
        saat_dilimi = 8
    
    bolge_bilgisi = None
    funding_bolgeleri = parametreler.get('funding_bolgeleri', [])
    for bolge in funding_bolgeleri:
        if bolge['baslangic'] <= pozisyon <= bolge['bitis']:
            bolge_bilgisi = bolge
            break
    
    col1, col2 = st.columns(2)
    
    with col1:
        if bolge_bilgisi:
            st.markdown(f"**Mevcut Bölge:** {bolge_bilgisi['etiket']}")
            st.markdown(f"**Funding Sıklığı:** {saat_dilimi} saat")
        else:
            st.markdown(f"**Pozisyon:** {pozisyon:.6f}")
            st.markdown(f"**Funding Sıklığı:** {saat_dilimi} saat (default)")
    
    with col2:
        if pozisyon < 0.2:
            pozisyon_aciklama = "🔴 Güçlü Short - Yüksek Sıklık"
        elif pozisyon < 0.4:
            pozisyon_aciklama = "🟠 Orta Short"
        elif pozisyon < 0.6:
            pozisyon_aciklama = "🟡 Nötr Bölge - Normal Sıklık"
        elif pozisyon < 0.8:
            pozisyon_aciklama = "🟢 Orta Long"
        else:
            pozisyon_aciklama = "🟢 Güçlü Long - Yüksek Sıklık"
        
        st.markdown(f"**Durum:** {pozisyon_aciklama}")
    
    try:
        hesaplamalar = funding_oran_hesaplamalari_dinamik(funding_orani, saat_dilimi, pozisyon)
    except Exception as e:
        st.error(f"Hesaplama hatası: {e}")
        hesaplamalar = {
            'saat_dilimi_orani': funding_orani,
            'gunluk_oran': funding_orani * (24 / saat_dilimi),
            'yillik_oran': funding_orani * (24 / saat_dilimi) * 365,
            'gunluk_kesim_sayisi': 24 / saat_dilimi
        }
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=f"{saat_dilimi} Saatlik Oran",
            value=f"{hesaplamalar['saat_dilimi_orani']:.6f}%",
            help=f"Her {saat_dilimi} saatte bir kesilecek"
        )
    
    with col2:
        st.metric(
            label="Günlük Oran", 
            value=f"{hesaplamalar['gunluk_oran']:.6f}%",
            help=f"Günde {hesaplamalar['gunluk_kesim_sayisi']:.1f} kez kesilir"
        )
    
    with col3:
        st.metric(
            label="Yıllık Oran",
            value=f"{hesaplamalar['yillik_oran']:.3f}%", 
            help="365 günde toplam funding"
        )
    
    with col4:
        # Funding miktarı (1000$ için)
        miktar_1000 = 1000 * (hesaplamalar['saat_dilimi_orani'] / 100)
        st.metric(
            label=f"1000$ için",
            value=f"${miktar_1000:.6f}",
            help=f"1000$ pozisyon için her {saat_dilimi} saatte"
        )
    
    st.info(f"💡 Bu pozisyonda funding her **{saat_dilimi} saat**te bir kesilir. Ekstrem pozisyonlarda sıklık artar!")
    
    fig_slider = go.Figure()
    
    fig_slider.add_trace(
        go.Scatter(
            x=x_degerleri,
            y=combined_curve,
            mode='lines',
            name='Funding Oranı',
            line=dict(color='#00D2FF', width=4, shape='spline'),
            hovertemplate='Pozisyon: %{x:.6f}<br>Funding: %{y:.6f}%<extra></extra>',
            fill='tonexty'
        )
    )
    
    if funding_bolgeleri:
        renk_paleti = [
            '#FFE5E5',  
            '#FFE5CC',  
            '#E5F3FF',
            '#E5FFE5', 
            '#F0E5FF'  
        ]
        
        for i, bolge in enumerate(funding_bolgeleri):
            renk = renk_paleti[i % len(renk_paleti)]
            
            fig_slider.add_vrect(
                x0=bolge['baslangic'], 
                x1=bolge['bitis'],
                fillcolor=renk,
                opacity=0.4,
                layer="below",
                line_width=0
            )
            
            orta_x = (bolge['baslangic'] + bolge['bitis']) / 2
            max_y = max(combined_curve)
            
            fig_slider.add_annotation(
                x=orta_x,
                y=max_y * 0.9,
                text=f"<b>{bolge['saat']}h</b><br>{bolge['etiket'].split('(')[0].strip()}",
                showarrow=False,
                font=dict(size=11, color='#2C3E50'),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#BDC3C7",
                borderwidth=1,
                borderpad=4
            )
    
    fig_slider.add_vline(
        x=pozisyon,
        line_color='#E74C3C',
        line_width=3,
        line_dash="solid",
        annotation_text=f"📍 {pozisyon:.6f}<br>⏱️ {saat_dilimi}h sıklık",
        annotation_position="top",
        annotation=dict(
            bgcolor="rgba(231, 76, 60, 0.9)",
            bordercolor="white",
            borderwidth=2,
            font=dict(color="white", size=12)
        )
    )
    
    fig_slider.add_trace(
        go.Scatter(
            x=[pozisyon],
            y=[funding_orani],
            mode='markers',
            marker=dict(
                color='#E74C3C', 
                size=15,
                symbol='circle',
                line=dict(color='white', width=3)
            ),
            name=f"Funding: {funding_orani:.6f}%",
            hovertemplate=f'<b>Seçilen Nokta</b><br>Pozisyon: {pozisyon:.6f}<br>Funding: {funding_orani:.6f}%<br>Sıklık: {saat_dilimi}h<extra></extra>',
            showlegend=False
        )
    )
    
    fig_slider.add_hline(y=0, line_color='white', line_width=2, opacity=0.8)
    
    fig_slider.update_layout(
        title=dict(
            text="<b>Seçilen Pozisyonda Dinamik Funding</b>",
            x=0.5,
            font=dict(size=16, color='white')
        ),
        xaxis_title="Pozisyon Oranı (0=Short, 1=Long)",
        yaxis_title="Funding Oranı (%)",
        height=400,
        template="plotly_dark",
        showlegend=False,
        paper_bgcolor='#1a1a1a',
        plot_bgcolor='#2d2d2d',
        margin=dict(t=60, b=60, l=60, r=60),
        font=dict(family="Arial", size=12, color='white')
    )
    
    fig_slider.update_xaxes(
        range=[0, 1], 
        tickformat='.3f',
        gridcolor='rgba(255,255,255,0.2)',
        title_font=dict(size=14, color='white'),
        tickfont=dict(color='white')
    )
    fig_slider.update_yaxes(
        tickformat='.4f',
        gridcolor='rgba(255,255,255,0.2)',
        title_font=dict(size=14, color='white'),
        tickfont=dict(color='white')
    )
    
    st.plotly_chart(fig_slider, use_container_width=True)
    
    return pozisyon, funding_orani, saat_dilimi


def parametre_duyarlilik_grafigi_yeni(temel_x, temel_y, varyasyon_verileri, parametre_ismi):

    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=temel_x,
            y=temel_y,
            mode='lines',
            name='Mevcut Ayar',
            line=dict(color=RENKLER['zero_line'], width=4),
            hovertemplate='Mevcut<br>Pozisyon: %{x:.3f}<br>Oran: %{y:.4f}%<extra></extra>'
        )
    )
    
    renkler = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    for i, (parametre_degeri, degerler) in enumerate(varyasyon_verileri.items()):
        fig.add_trace(
            go.Scatter(
                x=temel_x,
                y=degerler,
                mode='lines',
                name=f'{parametre_ismi} = {parametre_degeri:.3f}',
                line=dict(color=renkler[i % len(renkler)], width=2, dash='dash'),
                opacity=0.7,
                hovertemplate=f'{parametre_ismi} = {parametre_degeri:.3f}<br>Pozisyon: %{{x:.3f}}<br>Oran: %{{y:.4f}}%<extra></extra>'
            )
        )
    
    fig.add_hline(y=0, line_color=RENKLER['zero_line'], line_width=2, opacity=0.8)
    fig.add_vline(x=0.5, line_color=RENKLER['zero_line'], line_width=1, opacity=0.5)
    
    fig.update_layout(
        title=f"Parametre Duyarlılık Analizi - {parametre_ismi}",
        xaxis_title=METINLER['pozisyon_orani'],
        yaxis_title=METINLER['funding_orani'],
        template="plotly_dark",
        height=400,
        hovermode='x unified',
        paper_bgcolor='#1a1a1a',
        plot_bgcolor='#2d2d2d',
        font=dict(color='white')
    )
    
    fig.update_xaxes(range=[0, 1])
    
    return fig

def cap_etkisi_grafigi(x_degerleri, orijinal_curve, capli_curve, min_cap, max_cap):

    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=x_degerleri,
            y=orijinal_curve,
            mode='lines',
            name='Cap\'siz Orijinal',
            line=dict(color=RENKLER['neutral'], width=2, dash='dot'),
            opacity=0.6
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=x_degerleri,
            y=capli_curve,
            mode='lines',
            name='Cap Uygulanmış',
            line=dict(color=RENKLER['combined_curve'], width=3)
        )
    )

    fig.add_hline(
        y=min_cap,
        line_dash="dash",
        line_color=RENKLER['cap_lines'],
        line_width=2,
        annotation_text=f"Min Cap: {min_cap:.3f}%"
    )
    
    fig.add_hline(
        y=max_cap,
        line_dash="dash", 
        line_color=RENKLER['cap_lines'],
        line_width=2,
        annotation_text=f"Max Cap: {max_cap:.3f}%"
    )
    
    fig.add_hline(y=0, line_color=RENKLER['zero_line'], line_width=2, opacity=0.8)
    
    fig.update_layout(
        title="Cap Değerlerinin Etkisi",
        xaxis_title=METINLER['pozisyon_orani'],
        yaxis_title=METINLER['funding_orani'],
        template="plotly_dark",
        height=400,
        paper_bgcolor='#1a1a1a',
        plot_bgcolor='#2d2d2d',
        font=dict(color='white')
    )
    
    fig.update_xaxes(range=[0, 1])
    
    return fig

def istatistik_tablosu_olustur(istatistikler):

    import pandas as pd
    
    istatistik_df = pd.DataFrame([
        {"Metrik": "Minimum Oran", "Değer": f"{istatistikler['min']:.4f}%"},
        {"Metrik": "Maksimum Oran", "Değer": f"{istatistikler['max']:.4f}%"},
        {"Metrik": "Ortalama Oran", "Değer": f"{istatistikler['ortalama']:.4f}%"},
        {"Metrik": "Standart Sapma", "Değer": f"{istatistikler['standart_sapma']:.4f}%"},
        {"Metrik": "Değer Aralığı", "Değer": f"{istatistikler['aralik']:.4f}%"}
    ])
    
    return istatistik_df

def funding_hesaplama_tablosu(funding_orani, funding_saatleri):
  
    import pandas as pd
    from curve_functions import funding_oran_hesaplamalari
    
    tablo_verileri = []
    
    for saat in funding_saatleri:
        hesaplamalar = funding_oran_hesaplamalari(funding_orani, saat)
        tablo_verileri.append({
            "Saat Dilimi": f"{saat} Saat",
            "Saat Dilimi Oranı": f"{hesaplamalar['saat_dilimi_orani']:.4f}%",
            "Günlük Oran": f"{hesaplamalar['gunluk_oran']:.3f}%",
            "Yıllık Oran": f"{hesaplamalar['yillik_oran']:.1f}%",
            "1000$ için": f"${1000 * hesaplamalar['saat_dilimi_orani'] / 100:.2f}"
        })
    
    return pd.DataFrame(tablo_verileri)

def karsilastirma_grafigi_olustur_yeni(x_degerleri, senaryo_verileri):
  
    fig = go.Figure()
    
    renkler = [RENKLER['combined_curve'], RENKLER['short_curve'], 
              RENKLER['long_curve'], RENKLER['transition']]
    
    for i, (isim, degerler) in enumerate(senaryo_verileri.items()):
        fig.add_trace(
            go.Scatter(
                x=x_degerleri,
                y=degerler,
                mode='lines',
                name=isim,
                line=dict(color=renkler[i % len(renkler)], width=3),
                hovertemplate=f'{isim}<br>Pozisyon: %{{x:.3f}}<br>Değer: %{{y:.4f}}%<extra></extra>'
            )
        )
    
    fig.add_hline(y=0, line_color=RENKLER['zero_line'], line_width=2, opacity=0.8)
    fig.add_vline(x=0.5, line_color=RENKLER['zero_line'], line_width=1, opacity=0.5)
    
    fig.update_layout(
        title="Senaryo Karşılaştırması",
        xaxis_title=METINLER['pozisyon_orani'],
        yaxis_title=METINLER['funding_orani'],
        template="plotly_dark",
        height=400,
        hovermode='x unified',
        paper_bgcolor='#1a1a1a',
        plot_bgcolor='#2d2d2d',
        font=dict(color='white')
    )
    
    fig.update_xaxes(range=[0, 1])
    
    return fig

def gecis_bolgesi_detay_grafigi_yeni(x_degerleri, combined_curve, gecis_bilgileri):
  
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=x_degerleri,
            y=combined_curve,
            mode='lines',
            name='Funding Oranı',
            line=dict(color=RENKLER['combined_curve'], width=4)
        )
    )
    
    fig.add_vrect(
        x0=gecis_bilgileri['baslangic'], 
        x1=gecis_bilgileri['bitis'],
        fillcolor=RENKLER['transition'],
        opacity=0.2,
        layer="below",
        line_width=0
    )
    
    fig.add_vline(
        x=gecis_bilgileri['baslangic'],
        line_dash="dash",
        line_color=RENKLER['transition'],
        annotation_text="Geçiş Başlangıç"
    )
    
    fig.add_vline(
        x=gecis_bilgileri['bitis'],
        line_dash="dash", 
        line_color=RENKLER['transition'],
        annotation_text="Geçiş Bitiş"
    )
    
    fig.add_hline(y=0, line_color=RENKLER['zero_line'], line_width=2, opacity=0.8)
    fig.add_vline(x=0.5, line_color=RENKLER['zero_line'], line_width=1, opacity=0.5)
    
    fig.update_layout(
        title="Geçiş Bölgesi Detay Analizi",
        xaxis_title=METINLER['pozisyon_orani'],
        yaxis_title=METINLER['funding_orani'],
        template="plotly_dark",
        height=400,
        showlegend=False,
        paper_bgcolor='#1a1a1a',
        plot_bgcolor='#2d2d2d',
        font=dict(color='white')
    )
    
    fig.update_xaxes(range=[0, 1])
    
    return fig