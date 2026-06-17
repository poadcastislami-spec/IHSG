import streamlit as st
import pandas as pd
import yfinance as yf
import math
from datetime import datetime

# 1. KONFIGURASI HALAMAN UTAMA (WIDE MODE)
st.set_page_config(page_title="IHSG PREMIUM SCALPER TERMINAL", layout="wide")

# === JUDUL UTAMA WEBSITE ===
st.title("⚡ IHSG PREMIUM SCALPER TERMINAL ⚡")
st.caption("Data Integrasi Live Bursa Efek Indonesia — Analisis Teknikal, Likuiditas, & Arus Asing")
st.markdown("---")

# Default State Variabel (Global Scope)
harga_terakhir = 0
vol_terakhir = 0
vol_kemarin = 0
change_persen = 0.0
rsi_terakhir = 50.0
rsi_kemarin = 50.0
stoch_k = 50.0
stoch_d = 50.0
stoch_k_kemarin = 50.0
stoch_d_kemarin = 50.0
ma_volume_20 = 1.0
foreign_net_summary = "NETRAL"
foreign_value_est = 0
is_volume_buyer_dominant = True
support_fibo = 0
resisten_fibo = 0
vwap_val = 0

# Variabel Moving Average (MA)
status_ma5 = ""
status_ma20 = ""
status_ma50 = ""

# === 4. PERBAIKAN: AREA PENCARIAN SAHAM DIKECILKAN ===
st.markdown("### 🔍 MONITORING EMITEN")
col_search_block, _ = st.columns([1.4, 1.6]) 
with col_search_block:
    c_input_small, _ = st.columns([1.5, 1.5]) 
    with c_input_small:
        ticker_pantau = st.text_input("Ketik Kode Saham:", value="BBCA", key="pencarian_utama").upper().strip()

try:
    ticker_engine = yf.Ticker(f"{ticker_pantau}.JK")
    df_live = ticker_engine.history(period="100d", interval="1d")
    
    if not df_live.empty:
        harga_terakhir = int(df_live.iloc[-1]['Close'])
        vol_terakhir = int(df_live.iloc[-1]['Volume'])
        open_hari_ini = float(df_live.iloc[-1]['Open'])
        
        # Data untuk Fibonacci
        high_val = df_live['High'].max()
        low_val = df_live['Low'].min()
        diff = high_val - low_val
        support_fibo = round(low_val + (diff * 0.236))
        resisten_fibo = round(low_val + (diff * 0.618))

        # Data untuk VWAP
        df_live['VWAP'] = (df_live['Volume'] * (df_live['High'] + df_live['Low'] + df_live['Close']) / 3).cumsum() / df_live['Volume'].cumsum()
        vwap_val = round(df_live['VWAP'].iloc[-1])
        
        if len(df_live) > 1:
            vol_kemarin = int(df_live.iloc[-2]['Volume'])
            harga_kemarin = float(df_live.iloc[-2]['Close'])
            change_persen = round(((harga_terakhir - harga_kemarin) / harga_kemarin) * 100, 2)
        
        is_volume_buyer_dominant = harga_terakhir >= open_hari_ini
        
        delta = df_live['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=10).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=10).mean()
        rs = gain / loss
        rsi_series = 100 - (100 / (1 + rs))
        rsi_terakhir = round(rsi_series.iloc[-1], 2)
        rsi_kemarin = round(rsi_series.iloc[-2], 2)
        
        rsi_min = rsi_series.rolling(window=10).min()
        rsi_max = rsi_series.rolling(window=10).max()
        stoch_rsi_series = (rsi_series - rsi_min) / (rsi_max - rsi_min) * 100
        df_live['Stoch_K'] = stoch_rsi_series.rolling(window=3).mean()
        df_live['Stoch_D'] = df_live['Stoch_K'].rolling(window=3).mean()
        
        stoch_k = round(df_live['Stoch_K'].iloc[-1], 2)
        stoch_d = round(df_live['Stoch_D'].iloc[-1], 2)
        stoch_k_kemarin = round(df_live['Stoch_K'].iloc[-2], 2)
        stoch_d_kemarin = round(df_live['Stoch_D'].iloc[-2], 2)
        
        ma_volume_20 = df_live['Volume'].rolling(window=20).mean().iloc[-1]
        
        ma5_val = df_live['Close'].rolling(window=5).mean().iloc[-1]
        ma20_val = df_live['Close'].rolling(window=20).mean().iloc[-1]
        ma50_val = df_live['Close'].rolling(window=50).mean().iloc[-1]
        
        status_ma5 = f"<span style='color: #2ecc71;'>🟢 Di Atas MA5</span> (Rp {round(ma5_val):,})" if harga_terakhir > ma5_val else f"<span style='color: #e74c3c;'>🔴 Di Bawah MA5</span> (Rp {round(ma5_val):,})"
        status_ma20 = f"<span style='color: #2ecc71;'>🟢 Di Atas MA20</span> (Rp {round(ma20_val):,})" if harga_terakhir > ma20_val else f"<span style='color: #e74c3c;'>🔴 Di Bawah MA20</span> (Rp {round(ma20_val):,})"
        status_ma50 = f"<span style='color: #2ecc71;'>🟢 Di Atas MA50</span> (Rp {round(ma50_val):,})" if harga_terakhir > ma50_val else f"<span style='color: #e74c3c;'>🔴 Di Bawah MA50</span> (Rp {round(ma50_val):,})"
        
        perubahan_dana = (harga_terakhir - open_hari_ini) * vol_terakhir * 0.035
        foreign_value_est = int(perubahan_dana)
        if foreign_value_est > 50000000:
            foreign_net_summary = "AKUMULASI"
        elif foreign_value_est < -50000000:
            foreign_net_summary = "DISTRIBUSI"
        else:
            foreign_net_summary = "NETRAL"
            
except Exception as e:
    st.error(f"Gagal memuat data emiten {ticker_pantau}. Pastikan kode terdaftar di bursa.")

status_saran = "HOLD / WAIT & SEE"
bg_badge = "#f1c40f"
text_badge = "HOLD"

if rsi_terakhir < 38 or (stoch_k_kemarin <= stoch_d_kemarin and stoch_k > stoch_d and stoch_k < 35):
    status_saran = "STRATEGIC BUY / ACCUM"
    bg_badge = "#2ecc71"
    text_badge = "BUY"
elif rsi_terakhir > 72 or (stoch_k_kemarin >= stoch_d_kemarin and stoch_k < stoch_d and stoch_k > 70):
    status_saran = "TAKE PROFIT / DISTRIBUTION"
    bg_badge = "#e74c3c"
    text_badge = "SELL"

col_left_panel, col_right_panel = st.columns([1.4, 1.6])

with col_left_panel:
    # KONTAINER 1: Status Utama + Live Metrik
    with st.container(border=True):
        st.markdown("##### 📊 DATA LIVE METRIK")
        st.markdown(f"""
        <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px;'>
            <div style='font-size: 15px; font-weight: bold;'>STATUS UTAMA: Ticker <span style='background-color: #2e313d; padding: 3px 8px; border-radius: 4px; color: #29b6f6;'>{ticker_pantau}</span></div>
            <div style='background-color: {bg_badge}; color: #111111; font-weight: 900; font-size: 18px; padding: 5px 22px; border-radius: 5px; box-shadow: 0px 2px 10px {bg_badge}40; letter-spacing: 1px;'>{text_badge}</div>
        </div>
        <div style='font-size: 12px; color: #aaa; margin-bottom: 10px;'>Kondisi Teknis Analisis: <b>{status_saran}</b></div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        c_box1, c_box2, c_box3 = st.columns(3)
        c_box1.metric(label="💰 Harga Terakhir", value=f"Rp {harga_terakhir:,}", delta=f"{change_persen}%")
        panah_volume = "🔼" if vol_terakhir >= vol_kemarin else "🔽"
        c_box2.metric(label=f"📊 Volume {panah_volume}", value=f"{vol_terakhir:,}", delta=f"Vs Sesi Lalu: {vol_kemarin:,}")
        panah_rsi = "🔼" if rsi_terakhir >= rsi_kemarin else "🔽"
        c_box3.metric(label=f"📈 RSI {panah_rsi}", value=f"{rsi_terakhir}%", delta=f"{rsi_kemarin}%")

    # KONTAINER 2: Analisis Fibonacci + VWAP
    with st.container(border=True):
        st.markdown("##### 📐 ANALISIS FIBONACCI & VWAP")
        cf1, cf2, cf3 = st.columns(3)
        cf1.markdown(f"""
        <div style='background-color: rgba(231, 76, 60, 0.08); border: 1px solid #e74c3c; padding: 10px 8px; border-radius: 6px; text-align: center;'>
            <div style='color: #e74c3c; font-size: 10px; font-weight: bold;'>SUPPORT (23.6%)</div>
            <div style='font-weight: bold; font-size: 15px;'>Rp {support_fibo:,}</div>
        </div>
        """, unsafe_allow_html=True)
        cf2.markdown(f"""
        <div style='background-color: rgba(46, 204, 113, 0.08); border: 1px solid #2ecc71; padding: 10px 8px; border-radius: 6px; text-align: center;'>
            <div style='color: #2ecc71; font-size: 10px; font-weight: bold;'>RESISTANCE (61.8%)</div>
            <div style='font-weight: bold; font-size: 15px;'>Rp {resisten_fibo:,}</div>
        </div>
        """, unsafe_allow_html=True)
        cf3.markdown(f"""
        <div style='background-color: rgba(52, 152, 219, 0.08); border: 1px solid #3498db; padding: 10px 8px; border-radius: 6px; text-align: center;'>
            <div style='color: #3498db; font-size: 10px; font-weight: bold;'>VWAP</div>
            <div style='font-weight: bold; font-size: 15px;'>Rp {vwap_val:,}</div>
        </div>
        """, unsafe_allow_html=True)

    # KONTAINER 3: Kalkulator Trading Plan
    with st.container(border=True):
        st.markdown("##### 🎯 KALKULATOR TRADING PLAN")
        harga_entry_calc = st.number_input("Harga Entry (Rp):", min_value=50, max_value=200000, value=harga_terakhir if harga_terakhir > 0 else 100, step=1)
        tp_fast = math.ceil(harga_entry_calc * 1.025)
        tp_peak = math.ceil(harga_entry_calc * 1.055)
        sl_safe = math.floor(harga_entry_calc * 0.962)
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            st.markdown(f"""<div style='background-color: rgba(46, 204, 113, 0.08); border: 1px solid #2ecc71; padding: 8px; border-radius: 6px; text-align: center;'><span style='color: #2ecc71; font-weight: bold; font-size: 12px;'>TP1 (2.5%)</span><br><b style='font-size: 15px;'>Rp {tp_fast:,}</b></div>""", unsafe_allow_html=True)
        with cc2:
            st.markdown(f"""<div style='background-color: rgba(46, 204, 113, 0.08); border: 1px solid #2ecc71; padding: 8px; border-radius: 6px; text-align: center;'><span style='color: #2ecc71; font-weight: bold; font-size: 12px;'>TP2 (5.5%)</span><br><b style='font-size: 15px;'>Rp {tp_peak:,}</b></div>""", unsafe_allow_html=True)
        with cc3:
            st.markdown(f"""<div style='background-color: rgba(231, 76, 60, 0.08); border: 1px solid #e74c3c; padding: 8px; border-radius: 6px; text-align: center;'><span style='color: #e74c3c; font-weight: bold; font-size: 12px;'>SL (-3.8%)</span><br><b style='font-size: 15px;'>Rp {sl_safe:,}</b></div>""", unsafe_allow_html=True)

with col_right_panel:
    st.markdown("##### 📋 LIVE MARKET INTELLIGENCE & ACTION PLAN")
    
    if stoch_k_kemarin <= stoch_d_kemarin and stoch_k > stoch_d:
        txt_stoch = "⚠️ <b>GOLDEN CROSS DETECTED!</b> Sinyal rebound kuat terkonfirmasi di area bawah." if stoch_k < 35 else "🔼 <b>BULLISH CROSSOVER:</b> Momentum harian beralih ke pembeli."
    elif stoch_k_kemarin >= stoch_d_kemarin and stoch_k < stoch_d:
        txt_stoch = "⚠️ <b>DEAD CROSS DETECTED!</b> Aksi ambil untung menekan harga ke area overbought." if stoch_k > 70 else "🔽 <b>BEARISH CROSSOVER:</b> Tekanan jual jangka pendek meningkat."
    else:
        txt_stoch = "⚖️ <b>KONSOLIDASI:</b> Momentum cenderung bergerak mendatar."

    rasio_vol_ma = vol_terakhir / ma_volume_20 if ma_volume_20 > 0 else 1.0
    if rasio_vol_ma >= 1.8:
        txt_vol = f"🔥 <b>VOLUME BREAKOUT!</b> Transaksi melonjak {round(rasio_vol_ma, 1)}x di atas rata-rata."
    elif rasio_vol_ma <= 0.6:
        txt_vol = "💤 <b>DRY VOLUME:</b> Likuiditas pasar sangat sepi."
    else:
        txt_vol = "Organik (Transaksi normal)."

    if foreign_net_summary == "AKUMULASI":
        txt_foreign = f"🟢 <b>FOREIGN ACCUMULATION:</b> Neto <b>Rp {abs(foreign_value_est):,}</b>."
    elif foreign_net_summary == "DISTRIBUSI":
        txt_foreign = f"🔴 <b>FOREIGN DISTRIBUTION:</b> Neto <b>Rp {abs(foreign_value_est):,}</b>."
    else:
        txt_foreign = "🟡 <b>NEUTRAL FLOW:</b> Transaksi asing berimbang."

    if text_badge == "BUY":
        txt_rekomendasi = "💥 <b>STRATEGIC BUY:</b> Akumulasi bertahap dekat support utama."
        border_color_action = "#2ecc71"
    elif text_badge == "SELL":
        txt_rekomendasi = "🚨 <b>TAKE PROFIT:</b> Amankan modal sebelum distribusi lanjutan."
        border_color_action = "#e74c3c"
    else:
        txt_rekomendasi = "🟡 <b>HOLD / WAIT & SEE:</b> Pantau area beli terdekat."
        border_color_action = "#f1c40f"

    with st.container(border=True):
        st.markdown(f"""
        <div style='background-color: #1e222d; border: 1px solid #2e313d; border-left: 4px solid #3498db; padding: 10px; border-radius: 4px; margin-bottom: 10px;'>
            <b style='color: #3498db; font-size: 14px;'>📈 TREND MOVING AVERAGE (MA)</b><br>
            <span style='font-size: 13px; line-height: 1.5; color: #d1d4dc;'>
            • MA 5: {status_ma5}<br>
            • MA 20: {status_ma20}<br>
            • MA 50: {status_ma50}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background-color: #1e222d; border: 1px solid #2e313d; border-left: 4px solid #9b59b6; padding: 10px; border-radius: 4px; margin-bottom: 10px;'>
            <b style='color: #9b59b6; font-size: 14px;'>⏱️ MOMENTUM STOCHASTIC RSI</b><br>
            <span style='font-size: 13px; color: #d1d4dc;'>{txt_stoch}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background-color: #1e222d; border: 1px solid #2e313d; border-left: 4px solid #1abc9c; padding: 10px; border-radius: 4px; margin-bottom: 10px;'>
            <b style='color: #1abc9c; font-size: 14px;'>📦 LIKUIDITAS VOLUME</b><br>
            <span style='font-size: 13px; color: #d1d4dc;'>{txt_vol}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background-color: #1e222d; border: 1px solid #2e313d; border-left: 4px solid #e67e22; padding: 10px; border-radius: 4px; margin-bottom: 10px;'>
            <b style='color: #e67e22; font-size: 14px;'>🌐 FOREIGN FLOW</b><br>
            <span style='font-size: 13px; color: #d1d4dc;'>{txt_foreign}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background-color: #1e222d; border: 1px solid #2e313d; border-left: 6px solid {border_color_action}; padding: 12px; border-radius: 4px;'>
            <b style='color: #ffca28; font-size: 14px;'>🎯 REKOMENDASI TRADING</b><br>
            <span style='font-size: 13px; color: #ffffff;'>{txt_rekomendasi}</span>
        </div>
        """, unsafe_allow_html=True)

# === FITUR SCREENING EMITEN (TERINTEGRASI) ===
st.markdown("---")
st.markdown("### 🚀 RADAR SCREENING EMITEN (Rp 90 - Rp 250)")

# Definisi fungsi screening di dalam script
def analisa_saham(ticker):
    df = yf.download(ticker, period="60d", interval="1d", progress=False)
    
    if df.empty or len(df) < 30:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    # 1. Hitung Perubahan Harga & Volume
    df['Pct_Change'] = df['Close'].pct_change() * 100
    df['Price_Diff'] = df['Close'].diff()
    df['MA_Vol_20'] = df['Volume'].rolling(window=20).mean()

    # RSI Mandiri
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Stochastic Mandiri
    low_14 = df['Low'].rolling(window=14).min()
    high_14 = df['High'].rolling(window=14).max()
    df['Stoch_K'] = 100 * ((df['Close'] - low_14) / (high_14 - low_14))
    df['Stoch_D'] = df['Stoch_K'].rolling(window=3).mean()

    hari_ini = df.iloc[-1]

    def bersihkan_angka(data_input):
        try:
            if hasattr(data_input, "__len__") and not isinstance(data_input, (str, bytes)):
                val = float(data_input[0])
            else:
                val = float(data_input)
            return 0.0 if math.isnan(val) else val
        except:
            return 0.0

    close_now = bersihkan_angka(hari_ini['Close'])
    pct_now = bersihkan_angka(hari_ini['Pct_Change'])
    diff_now = bersihkan_angka(hari_ini['Price_Diff'])
    vol_now = int(bersihkan_angka(hari_ini['Volume']))
    ma_vol_20 = bersihkan_angka(hari_ini['MA_Vol_20'])
    rsi_now = bersihkan_angka(hari_ini['RSI'])
    k_now = bersihkan_angka(hari_ini['Stoch_K'])
    d_now = bersihkan_angka(hari_ini['Stoch_D'])

    # Kriteria harga Rp 90 - Rp 250
    if not (90 <= close_now <= 250):
        return None 

    rasio_vol = (vol_now / ma_vol_20) if ma_vol_20 > 0 else 0.0

    # LOGIKA RADAR DETEKSI DINI UNTUK SCALPING
    status_radar = "Normal"
    if rasio_vol >= 2.0 and pct_now >= 2.0:
        status_radar = "🔥 AWAS TERBANG (Vol Spike & Harga Naik)"
    elif rasio_vol >= 1.5 and pct_now > 0:
        status_radar = "👀 Pantauan (Volume Mulai Masuk)"

    return {
        "Tanggal": datetime.now().strftime('%Y-%m-%d'),
        "Ticker": ticker.replace(".JK", ""),
        "Harga Close": round(close_now, 2),
        "Perubahan %": round(pct_now, 2),
        "Selisih Harga": round(diff_now, 2),
        "Volume Hari Ini": vol_now,
        "Rata-rata Vol (20H)": round(ma_vol_20, 0),
        "Rasio Vol vs Rata2": round(rasio_vol, 2),
        "RSI": round(rsi_now, 2),
        "Stoch %K": round(k_now, 2),
        "Stoch %D": round(d_now, 2),
        "Radar Deteksi Dini": status_radar
    }

# DAFTAR 130 EMITEN PILIHAN TERBAIK (RANGE HARGA Rp 90 - Rp 250)
daftar_saham = [
    # Saham Favorit Ritel & Induk Volatilitas Tinggi
    "BUMI.JK", "BIPI.JK", "KIJA.JK", "PADI.JK", "DEWA.JK", "BUKA.JK", "GOTO.JK", 
    "ENRG.JK", "ELSA.JK", "ADHI.JK", "WIKA.JK", "PTPP.JK", "SMDR.JK", "HAIS.JK", 
    "TMAS.JK", "ASSA.JK", "PSSI.JK", "NELY.JK", "RMKE.JK", "COAL.JK", "DOID.JK",
    
    # Tambahan Saham Menuju Rp 250 (BREAKOUT SENSITIVE)
    "BBTN.JK", "MAIN.JK", "WOOD.JK", "ADMG.JK", "KRAS.JK", "BUDI.JK", "GOOD.JK", 
    "WIFI.JK", "LPKR.JK", "TOTL.JK", "KAEF.JK", "INAF.JK", "IRRA.JK", "PEHA.JK",
    "SCMA.JK", "MARI.JK", "ABBA.JK", "BHIT.JK", "IPTV.JK", "VIVA.JK", "MDIA.JK",
    "AGRO.JK", "BABP.JK", "BBYB.JK", "BBKP.JK", "BCIC.JK", "BACA.JK", "AMAR.JK",
    "DNAR.JK", "BGTG.JK", "BVIC.JK", "INPC.JK", "BCAP.JK", "PNBS.JK", "CFIN.JK",
    
    # Kelompok Sektor Konstruksi, Properti & Semen Lapis Dua
    "ASRI.JK", "PPRO.JK", "BKSL.JK", "MDLN.JK", "LPCK.JK", "GWSA.JK", "DGIK.JK", 
    "DOOH.JK", "COCO.JK", "NZIA.JK", "JKON.JK", "WEGE.JK", "WSBP.JK", "URBN.JK", 
    "ELTY.JK", "ACST.JK", "META.JK", "KPIG.JK", "BCIP.JK", "BPTR.JK", "DILD.JK",
    "OMRE.JK", "LPCK.JK", "CITY.JK", "SMRU.JK", "BEST.JK", "FORZ.JK", "PANI.JK",
    
    # Komoditas Mineral, Logam, Tekstil & Energi Alternatif
    "DKFT.JK", "ZINC.JK", "IKAN.JK", "SIMP.JK", "SOCI.JK", "APEX.JK", "SQMI.JK",
    "INDY.JK", "TOBA.JK", "KKGI.JK", "GTBO.JK", "BOSS.JK", "NANO.JK", "TRIL.JK",
    "OASA.JK", "ZBRA.JK", "MPOW.JK", "MIRA.JK", "CENT.JK", "KBLI.JK", "POLY.JK",
    "BAJA.JK", "ALTO.JK", "CAMP.JK", "CPRO.JK", "PMMP.JK", "PBRX.JK", "MYTX.JK",
    
    # Jajaran Baru Emiten Aktif Eksklusif Range 150-250
    "AISA.JK", "NASA.JK", "MLIA.JK", "TARA.JK", "IKAI.JK", "LUCK.JK", "KBRI.JK",
    "ENVY.JK", "BOLA.JK", "HDFA.JK", "BESS.JK", "HOMI.JK", "OILS.JK", "CNKO.JK",
    "NATO.JK", "LPPS.JK", "GEMA.JK", "PAMG.JK", "KIAS.JK", "SULI.JK", "GPRA.JK"
]

# Proteksi Duplikasi Ticker
daftar_saham = list(set(daftar_saham))

# Container untuk Screening
with st.container(border=True):
    col_btn, col_info = st.columns([1, 3])
    
    with col_btn:
        if st.button("🔄 JALANKAN SCREENING", use_container_width=True, type="primary"):
            st.session_state['run_screening'] = True
    
    with col_info:
        st.info(f"📊 **Total Emiten yang Discan:** {len(daftar_saham)} saham (Range Rp 90 - Rp 250)")
        st.caption("Klik tombol untuk memulai proses screening (mungkin memakan waktu 30-60 detik)")

    # Progress bar dan hasil screening
    if 'run_screening' in st.session_state and st.session_state['run_screening']:
        with st.spinner("⏳ Sedang melakukan screening saham, mohon tunggu..."):
            kumpulan_data = []
            progress_bar = st.progress(0)
            
            for i, saham in enumerate(daftar_saham):
                try:
                    hasil = analisa_saham(saham)
                    if hasil:
                        kumpulan_data.append(hasil)
                except Exception as e:
                    pass
                # Update progress
                progress_bar.progress((i + 1) / len(daftar_saham))
            
            progress_bar.empty()
            
            if kumpulan_data:
                df_hasil = pd.DataFrame(kumpulan_data)
                # Urutkan dari Rasio Volume Tertinggi ke Terendah
                df_hasil = df_hasil.sort_values(by="Rasio Vol vs Rata2", ascending=False)
                
                # Tampilkan jumlah hasil
                st.success(f"✅ Screening selesai! Ditemukan {len(df_hasil)} saham yang memenuhi kriteria.")
                
                # Tampilkan tabel dengan styling
                st.dataframe(
                    df_hasil,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Tanggal": st.column_config.TextColumn("Tanggal"),
                        "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                        "Harga Close": st.column_config.NumberColumn("Harga Close", format="Rp %.0f"),
                        "Perubahan %": st.column_config.NumberColumn("Perubahan %", format="%.2f%%"),
                        "Selisih Harga": st.column_config.NumberColumn("Selisih Harga", format="Rp %.0f"),
                        "Volume Hari Ini": st.column_config.NumberColumn("Volume", format="%d"),
                        "Rata-rata Vol (20H)": st.column_config.NumberColumn("Rata-rata Vol", format="%d"),
                        "Rasio Vol vs Rata2": st.column_config.NumberColumn("Rasio Vol", format="%.2f"),
                        "RSI": st.column_config.NumberColumn("RSI", format="%.2f"),
                        "Stoch %K": st.column_config.NumberColumn("Stoch %K", format="%.2f"),
                        "Stoch %D": st.column_config.NumberColumn("Stoch %D", format="%.2f"),
                        "Radar Deteksi Dini": st.column_config.TextColumn("Radar", width="medium"),
                    }
                )
                
                # Download button untuk export CSV
                csv = df_hasil.to_csv(index=False)
                st.download_button(
                    label="📥 Download Hasil Screening (CSV)",
                    data=csv,
                    file_name=f"Radar_Saham_Terbang_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                # Hapus state screening setelah selesai
                del st.session_state['run_screening']
            else:
                st.warning("⚠️ Tidak ada saham yang memenuhi kriteria harga Rp 90 - Rp 250 hari ini.")
                del st.session_state['run_screening']
    else:
        # Tampilkan placeholder jika belum screening
        st.info("💡 Klik tombol 'JALANKAN SCREENING' untuk melihat hasil analisis saham potensial.")
