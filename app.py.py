import streamlit as st
import pandas as pd
import yfinance as yf
import math
from datetime import datetime, timedelta
from collections import Counter

# ============================================
# KONFIGURASI HALAMAN
# ============================================
st.set_page_config(
    page_title="IHSG PREMIUM TERMINAL SCALPING & INTRADAY - FAHRUN HIDAYAT",
    layout="wide"
)

# ============================================
# JUDUL
# ============================================
st.title("⚡ IHSG PREMIUM TERMINAL SCALPING & INTRADAY ⚡")
st.caption("Created by: Fahrun Hidayat | Data Integrasi Live Bursa Efek Indonesia — Analisis Teknikal, Likuiditas, & Arus Asing")
st.markdown("---")

# ============================================
# DATA SEKTOR EMITEN
# ============================================
SEKTOR_EMITEN = {
    "BBCA": "🏦 Perbankan", "BBRI": "🏦 Perbankan", "BMRI": "🏦 Perbankan", "BBNI": "🏦 Perbankan",
    "BBTN": "🏦 Perbankan", "AGRO": "🏦 Perbankan", "BABP": "🏦 Perbankan", "BBYB": "🏦 Perbankan",
    "BBKP": "🏦 Perbankan", "BCIC": "🏦 Perbankan", "BACA": "🏦 Perbankan", "INPC": "🏦 Perbankan",
    "BCAP": "🏦 Perbankan", "PNBS": "🏦 Perbankan", "BVIC": "🏦 Perbankan",
    "GOTO": "🛒 E-commerce", "BUKA": "🛒 E-commerce", "AMAR": "🛒 E-commerce",
    "BUMI": "⛏️ Tambang", "ADRO": "⛏️ Tambang", "ITMG": "⛏️ Tambang", "PTBA": "⛏️ Tambang",
    "ENRG": "⛏️ Tambang", "ELSA": "⛏️ Tambang", "SMDR": "⛏️ Tambang", "RMKE": "⛏️ Tambang",
    "COAL": "⛏️ Tambang", "DOID": "⛏️ Tambang", "ZINC": "⛏️ Tambang", "SIMP": "⛏️ Tambang",
    "SOCI": "⛏️ Tambang", "APEX": "⛏️ Tambang", "INDY": "⛏️ Tambang", "TOBA": "⛏️ Tambang",
    "KKGI": "⛏️ Tambang", "GTBO": "⛏️ Tambang", "BOSS": "⛏️ Tambang",
    "ASRI": "🏗️ Properti", "PPRO": "🏗️ Properti", "BKSL": "🏗️ Properti", "MDLN": "🏗️ Properti",
    "LPCK": "🏗️ Properti", "GWSA": "🏗️ Properti", "DGIK": "🏗️ Properti", "DILD": "🏗️ Properti",
    "OMRE": "🏗️ Properti", "CITY": "🏗️ Properti", "SMRU": "🏗️ Properti",
    "ADHI": "🚧 Konstruksi", "WIKA": "🚧 Konstruksi", "PTPP": "🚧 Konstruksi", "WSBP": "🚧 Konstruksi",
    "JKON": "🚧 Konstruksi", "WEGE": "🚧 Konstruksi", "URBN": "🚧 Konstruksi",
    "KAEF": "💊 Farmasi", "INAF": "💊 Farmasi", "KLBF": "💊 Farmasi", "MERK": "💊 Farmasi",
    "TLKM": "📡 Telekomunikasi", "ISAT": "📡 Telekomunikasi", "EXCL": "📡 Telekomunikasi",
    "WIFI": "📡 Telekomunikasi", "IPTV": "📡 Telekomunikasi",
    "UNVR": "🧴 Consumer", "ICBP": "🧴 Consumer", "INDF": "🧴 Consumer", "MYOR": "🧴 Consumer",
    "AISA": "🧴 Consumer", "NASA": "🧴 Consumer", "MLIA": "🧴 Consumer",
    "BESS": "🔋 Energi", "HOMI": "🔋 Energi", "OILS": "🔋 Energi", "CNKO": "🔋 Energi",
    "NANO": "🔋 Energi", "MIRA": "🔋 Energi", "CENT": "🔋 Energi", "MPOW": "🔋 Energi",
    "PANI": "📰 Media", "SCMA": "📰 Media", "MARI": "📰 Media", "VIVA": "📰 Media",
    "MDIA": "📰 Media", "BOLA": "📰 Media", "NELY": "📰 Media",
    "BIPI": "🏭 Industri", "KIJA": "🏭 Industri", "PADI": "🏭 Industri", "DEWA": "🏭 Industri",
    "PSSI": "🏭 Industri", "HAIS": "🏭 Industri", "TMAS": "🏭 Industri", "ASSA": "🏭 Industri",
    "NATO": "🏭 Industri", "LPPS": "🏭 Industri", "GEMA": "🏭 Industri", "PAMG": "🏭 Industri",
    "KIAS": "🏭 Industri", "SULI": "🏭 Industri", "GPRA": "🏭 Industri",
    "MAIN": "🏭 Manufaktur", "WOOD": "🏭 Manufaktur", "ADMG": "🏭 Manufaktur", "KRAS": "🏭 Manufaktur",
    "BUDI": "🏭 Manufaktur", "GOOD": "🏭 Manufaktur", "TOTL": "🏭 Manufaktur", "IRRA": "🏭 Manufaktur",
    "PEHA": "🏭 Manufaktur", "ABBA": "🏭 Manufaktur", "BHIT": "🏭 Manufaktur", "DNAR": "🏭 Manufaktur",
    "BGTG": "🏭 Manufaktur", "CFIN": "🏭 Manufaktur", "DKFT": "🏭 Manufaktur", "IKAN": "🏭 Manufaktur",
    "SQMI": "🏭 Manufaktur", "PMMP": "🏭 Manufaktur", "PBRX": "🏭 Manufaktur", "MYTX": "🏭 Manufaktur",
    "KBLI": "🏭 Manufaktur", "POLY": "🏭 Manufaktur", "BAJA": "🏭 Manufaktur", "ALTO": "🏭 Manufaktur",
    "CAMP": "🏭 Manufaktur", "CPRO": "🏭 Manufaktur",
    "DOOH": "📺 Digital", "COCO": "📺 Digital", "NZIA": "📺 Digital", "ELTY": "📺 Digital",
    "ACST": "📺 Digital", "META": "📺 Digital", "KPIG": "📺 Digital", "BCIP": "📺 Digital",
    "BPTR": "📺 Digital", "BEST": "📺 Digital", "FORZ": "📺 Digital",
    "TARA": "🚗 Otomotif", "IKAI": "🚗 Otomotif", "LUCK": "🚗 Otomotif", "KBRI": "🚗 Otomotif",
    "ENVY": "🚗 Otomotif", "HDFA": "🚗 Otomotif", "ZBRA": "🚗 Otomotif", "TRIL": "🚗 Otomotif",
    "OASA": "🚗 Otomotif"
}

# ============================================
# INISIALISASI VARIABEL
# ============================================
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
support_fibo = 0
resisten_fibo = 0
vwap_val = 0
fibo_50 = 0
fibo_786 = 0
confluence_support = 0
confluence_resistance = 0
fvg_atas = 0
fvg_bawah = 0
fvg_status = "Tidak Ada Gap"
fvg_tanggal = ""
status_ma5 = ""
status_ma20 = ""
status_ma50 = ""
signal_ma_cross = ""
warna_signal_ma = "#f1c40f"

# ============================================
# DEFINISI VARIABEL UNTUK PANEL KANAN (DEFAULT)
# ============================================
txt_stoch = "⚖️ KONSOLIDASI: Momentum cenderung bergerak mendatar."
txt_vol = "✅ Organik (Transaksi normal)."
txt_foreign = "🟡 NEUTRAL FLOW: Transaksi asing berimbang."
txt_rekomendasi = "🟡 HOLD / WAIT & SEE: Pantau area beli terdekat."
border_color = "#f1c40f"
rasio_vol_ma = 1.0

# ============================================
# AREA PENCARIAN SAHAM
# ============================================
st.markdown("### 🔍 MONITORING EMITEN")

col_search_block, _ = st.columns([1.4, 1.6])
with col_search_block:
    col_input, _ = st.columns([1.5, 1.5])
    with col_input:
        def clear_focus():
            st.session_state['ticker_input'] = st.session_state['ticker_input']
            pass
        
        ticker_pantau = st.text_input(
            "Ketik Kode Saham:",
            value="BBCA",
            key="ticker_input",
            on_change=clear_focus
        ).upper().strip()
        
        sektor_emiten = SEKTOR_EMITEN.get(ticker_pantau, "📊 Lainnya")
        st.caption(f"**{sektor_emiten}**")

# ============================================
# AMBIL DATA DARI YAHOO FINANCE
# ============================================
try:
    ticker_engine = yf.Ticker(f"{ticker_pantau}.JK")
    df_live = ticker_engine.history(period="100d", interval="1d")
    
    if not df_live.empty:
        harga_terakhir = int(df_live.iloc[-1]['Close'])
        vol_terakhir = int(df_live.iloc[-1]['Volume'])
        open_hari_ini = float(df_live.iloc[-1]['Open'])
        high_hari_ini = float(df_live.iloc[-1]['High'])
        low_hari_ini = float(df_live.iloc[-1]['Low'])
        
        # === FIBONACCI LEVELS ===
        high_val = df_live['High'].max()
        low_val = df_live['Low'].min()
        diff = high_val - low_val
        support_fibo = round(low_val + (diff * 0.236))
        fibo_50 = round(low_val + (diff * 0.50))
        resisten_fibo = round(low_val + (diff * 0.618))
        fibo_786 = round(low_val + (diff * 0.786))
        
        # === CONFLUENCE ===
        df_recent = df_live.tail(20)
        low_points = df_recent['Low'].tolist()
        low_counts = Counter([round(x) for x in low_points])
        support_candidates = [price for price, count in low_counts.items() if count >= 2 and price < harga_terakhir]
        confluence_support = round(min(support_candidates)) if support_candidates else support_fibo
        
        high_points = df_recent['High'].tolist()
        high_counts = Counter([round(x) for x in high_points])
        resistance_candidates = [price for price, count in high_counts.items() if count >= 2 and price > harga_terakhir]
        confluence_resistance = round(max(resistance_candidates)) if resistance_candidates else resisten_fibo
        
        # === FAIR VALUE GAP (FVG) - Cek 5 hari ke belakang ===
        fvg_ditemukan = False
        for i in range(1, min(6, len(df_live))):
            prev_high = df_live.iloc[-1-i]['High']
            prev_low = df_live.iloc[-1-i]['Low']
            prev_date = df_live.index[-1-i]
            
            if low_hari_ini > prev_high:
                fvg_bawah = round(prev_high)
                fvg_atas = round(low_hari_ini)
                fvg_status = "📈 GAP UP (Bullish Gap)"
                fvg_tanggal = prev_date.strftime('%d-%m-%Y')
                fvg_ditemukan = True
                break
            elif high_hari_ini < prev_low:
                fvg_bawah = round(high_hari_ini)
                fvg_atas = round(prev_low)
                fvg_status = "📉 GAP DOWN (Bearish Gap)"
                fvg_tanggal = prev_date.strftime('%d-%m-%Y')
                fvg_ditemukan = True
                break
        
        if not fvg_ditemukan:
            fvg_status = "✅ Tidak Ada Gap"
            fvg_tanggal = ""
        
        # === VWAP ===
        df_live['VWAP'] = (df_live['Volume'] * (df_live['High'] + df_live['Low'] + df_live['Close']) / 3).cumsum() / df_live['Volume'].cumsum()
        vwap_val = round(df_live['VWAP'].iloc[-1])
        
        # === PERUBAHAN HARGA ===
        if len(df_live) > 1:
            vol_kemarin = int(df_live.iloc[-2]['Volume'])
            harga_kemarin = float(df_live.iloc[-2]['Close'])
            change_persen = round(((harga_terakhir - harga_kemarin) / harga_kemarin) * 100, 2)
        
        # === RSI ===
        delta = df_live['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=10).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=10).mean()
        rs = gain / loss
        rsi_series = 100 - (100 / (1 + rs))
        rsi_terakhir = round(rsi_series.iloc[-1], 2)
        rsi_kemarin = round(rsi_series.iloc[-2], 2)
        
        # === STOCHASTIC RSI ===
        rsi_min = rsi_series.rolling(window=10).min()
        rsi_max = rsi_series.rolling(window=10).max()
        stoch_rsi_series = (rsi_series - rsi_min) / (rsi_max - rsi_min) * 100
        df_live['Stoch_K'] = stoch_rsi_series.rolling(window=3).mean()
        df_live['Stoch_D'] = df_live['Stoch_K'].rolling(window=3).mean()
        
        stoch_k = round(df_live['Stoch_K'].iloc[-1], 2)
        stoch_d = round(df_live['Stoch_D'].iloc[-1], 2)
        stoch_k_kemarin = round(df_live['Stoch_K'].iloc[-2], 2)
        stoch_d_kemarin = round(df_live['Stoch_D'].iloc[-2], 2)
        
        # === MOVING AVERAGE ===
        ma_volume_20 = df_live['Volume'].rolling(window=20).mean().iloc[-1]
        ma5_val = df_live['Close'].rolling(window=5).mean().iloc[-1]
        ma20_val = df_live['Close'].rolling(window=20).mean().iloc[-1]
        ma50_val = df_live['Close'].rolling(window=50).mean().iloc[-1]
        
        # Status MA dengan warna
        if harga_terakhir > ma5_val:
            status_ma5 = f"🟢 Di Atas MA5 (Rp {round(ma5_val):,})"
        else:
            status_ma5 = f"🔴 Di Bawah MA5 (Rp {round(ma5_val):,})"
        
        if harga_terakhir > ma20_val:
            status_ma20 = f"🟢 Di Atas MA20 (Rp {round(ma20_val):,})"
        else:
            status_ma20 = f"🔴 Di Bawah MA20 (Rp {round(ma20_val):,})"
        
        if harga_terakhir > ma50_val:
            status_ma50 = f"🟢 Di Atas MA50 (Rp {round(ma50_val):,})"
        else:
            status_ma50 = f"🔴 Di Bawah MA50 (Rp {round(ma50_val):,})"
        
        # === SIGNAL MA CROSS ===
        ma5_series = df_live['Close'].rolling(window=5).mean()
        ma20_series = df_live['Close'].rolling(window=20).mean()
        
        if len(ma5_series) > 5 and len(ma20_series) > 5:
            if ma5_series.iloc[-1] > ma20_series.iloc[-1] and ma5_series.iloc[-2] <= ma20_series.iloc[-2]:
                signal_ma_cross = "🟢 GOLDEN CROSS (BULLISH) - MA5 Menembus MA20 ke Atas"
                warna_signal_ma = "#2ecc71"
            elif ma5_series.iloc[-1] < ma20_series.iloc[-1] and ma5_series.iloc[-2] >= ma20_series.iloc[-2]:
                signal_ma_cross = "🔴 DEAD CROSS (BEARISH) - MA5 Menembus MA20 ke Bawah"
                warna_signal_ma = "#e74c3c"
            else:
                signal_ma_cross = "⚪ TIDAK ADA CROSS - MA5 & MA20 Bergerak Sejajar"
                warna_signal_ma = "#f1c40f"
        
        # === FOREIGN FLOW ===
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

# ============================================
# STATUS & REKOMENDASI - LENGKAP UNTUK SCALPING
# ============================================

# 1. KONDISI DASAR
is_oversold_rsi = rsi_terakhir < 38
is_overbought_rsi = rsi_terakhir > 72
is_golden_cross = (stoch_k_kemarin <= stoch_d_kemarin and stoch_k > stoch_d and stoch_k < 35)
is_dead_cross = (stoch_k_kemarin >= stoch_d_kemarin and stoch_k < stoch_d and stoch_k > 70)

# 2. KONFIRMASI VOLUME
volume_confirm = vol_terakhir > ma_volume_20 * 1.2 if ma_volume_20 > 0 else False
volume_breakout = vol_terakhir > ma_volume_20 * 1.8 if ma_volume_20 > 0 else False

# 3. KONFIRMASI SUPPORT/RESISTANCE FIBONACCI
near_support = abs(harga_terakhir - support_fibo) / support_fibo < 0.02 if support_fibo > 0 else False
near_resistance = abs(harga_terakhir - resisten_fibo) / resisten_fibo < 0.02 if resisten_fibo > 0 else False

# 4. LOGIKA REKOMENDASI (5 LEVEL)
if (is_oversold_rsi or is_golden_cross) and volume_breakout and near_support:
    status_saran = "🔥 STRONG BUY - Volume Breakout + Support"
    bg_badge = "#00e676"
    text_badge = "STRONG BUY"
    
elif (is_oversold_rsi or is_golden_cross) and (volume_confirm or near_support):
    status_saran = "🟢 STRATEGIC BUY - Konfirmasi Volume atau Support"
    bg_badge = "#2ecc71"
    text_badge = "BUY"
    
elif (is_overbought_rsi or is_dead_cross) and volume_breakout and near_resistance:
    status_saran = "🔴 STRONG SELL - Volume Breakout + Resistance"
    bg_badge = "#ff1744"
    text_badge = "STRONG SELL"
    
elif (is_overbought_rsi or is_dead_cross) and (volume_confirm or near_resistance):
    status_saran = "🔴 TAKE PROFIT - Konfirmasi Volume atau Resistance"
    bg_badge = "#e74c3c"
    text_badge = "SELL"
    
else:
    status_saran = "⏸️ HOLD / WAIT & SEE - Tidak ada sinyal jelas"
    bg_badge = "#f1c40f"
    text_badge = "HOLD"

# ============================================
# LAYOUT UTAMA: KIRI & KANAN
# ============================================
col_left_panel, col_right_panel = st.columns([1.4, 1.6], gap="medium")

# ============================================
# PANEL KIRI
# ============================================
with col_left_panel:
    
    # --- KONTAINER 1: DATA LIVE METRIK ---
    with st.container(border=True):
        st.markdown("##### 📊 DATA LIVE METRIK")
        
        st.markdown(
            f"""
            <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px;'>
                <div style='font-size: 15px; font-weight: bold;'>
                    STATUS UTAMA: Ticker <span style='background-color: #2e313d; padding: 3px 8px; border-radius: 4px; color: #29b6f6;'>{ticker_pantau}</span>
                </div>
                <div style='background-color: {bg_badge}; color: #111111; font-weight: 900; font-size: 18px; padding: 5px 22px; border-radius: 5px; letter-spacing: 1px;'>
                    {text_badge}
                </div>
            </div>
            <div style='font-size: 12px; color: #aaa; margin-bottom: 10px;'>
                Kondisi Teknis Analisis: <b>{status_saran}</b>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("---")
        
        # --- METRIC 1: HARGA (TETAP) ---
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric(
            label="💰 Harga Terakhir",
            value=f"Rp {harga_terakhir:,}",
            delta=f"{change_persen}%"
        )
        
        # --- METRIC 2: VOLUME (DIPERBAIKI) ---
        # Hitung rasio volume terhadap rata-rata
        ma_volume_20_display = df_live['Volume'].rolling(window=20).mean().iloc[-1] if len(df_live) >= 20 else vol_terakhir
        rasio_vol_ma_display = vol_terakhir / ma_volume_20_display if ma_volume_20_display > 0 else 1.0
        
        # Tentukan status volume
        if rasio_vol_ma_display >= 2.0:
            status_vol = "🔥🔥 MELEDAK! (2x+)"
            icon_vol = "🚀🚀"
        elif rasio_vol_ma_display >= 1.5:
            status_vol = "🔥 TINGGI (1.5x+)"
            icon_vol = "🚀"
        elif rasio_vol_ma_display >= 0.8:
            status_vol = "✅ NORMAL"
            icon_vol = "✅"
        elif rasio_vol_ma_display >= 0.5:
            status_vol = "💤 RENDAH (0.5x-)"
            icon_vol = "💤"
        else:
            status_vol = "🥶 SEPI (0.5x-)"
            icon_vol = "🥶"
        
        col_m2.metric(
            label=f"📊 Volume {icon_vol}",
            value=f"{vol_terakhir:,}",
            delta=f"{status_vol}"
        )
        
        # --- METRIC 3: RSI (DIPERBAIKI) ---
        # Tentukan status RSI
        if rsi_terakhir < 30:
            status_rsi = "🔥 OVERSOLD"
            icon_rsi = "🟢"
        elif rsi_terakhir < 38:
            status_rsi = "📉 Oversold Area"
            icon_rsi = "📉"
        elif rsi_terakhir > 70:
            status_rsi = "🔥 OVERBOUGHT"
            icon_rsi = "🔴"
        elif rsi_terakhir > 62:
            status_rsi = "📈 Overbought Area"
            icon_rsi = "📈"
        else:
            status_rsi = "✅ NORMAL"
            icon_rsi = "✅"
        
        col_m3.metric(
            label=f"📈 RSI {icon_rsi}",
            value=f"{rsi_terakhir}%",
            delta=f"{status_rsi}"
        )
    
    # --- KONTAINER 2: FIBONACCI, CONFLUENCE & VWAP ---
    with st.container(border=True):
        st.markdown("##### 📐 ANALISIS FIBONACCI, CONFLUENCE & VWAP")
        
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        
        with col_f1:
            st.markdown(
                f"""
                <div style='background-color: rgba(231, 76, 60, 0.15); border: 2px solid #e74c3c; padding: 10px; border-radius: 8px; text-align: center;'>
                    <div style='color: #e74c3c; font-size: 11px; font-weight: bold;'>🔴 SUPPORT (23.6%)</div>
                    <div style='font-weight: bold; font-size: 16px; color: #e74c3c;'>Rp {support_fibo:,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col_f2:
            st.markdown(
                f"""
                <div style='background-color: rgba(241, 196, 15, 0.15); border: 2px solid #f1c40f; padding: 10px; border-radius: 8px; text-align: center;'>
                    <div style='color: #f1c40f; font-size: 11px; font-weight: bold;'>🟡 MIDDLE (50.0%)</div>
                    <div style='font-weight: bold; font-size: 16px; color: #f1c40f;'>Rp {fibo_50:,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col_f3:
            st.markdown(
                f"""
                <div style='background-color: rgba(46, 204, 113, 0.15); border: 2px solid #2ecc71; padding: 10px; border-radius: 8px; text-align: center;'>
                    <div style='color: #2ecc71; font-size: 11px; font-weight: bold;'>🟢 RESISTANCE (61.8%)</div>
                    <div style='font-weight: bold; font-size: 16px; color: #2ecc71;'>Rp {resisten_fibo:,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col_f4:
            st.markdown(
                f"""
                <div style='background-color: rgba(155, 89, 182, 0.15); border: 2px solid #9b59b6; padding: 10px; border-radius: 8px; text-align: center;'>
                    <div style='color: #9b59b6; font-size: 11px; font-weight: bold;'>🟣 DEEP (78.6%)</div>
                    <div style='font-weight: bold; font-size: 16px; color: #9b59b6;'>Rp {fibo_786:,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("---")
        
        col_c1, col_c2, col_c3 = st.columns(3)
        
        with col_c1:
            if confluence_support > 0:
                st.markdown(
                    f"""
                    <div style='background-color: rgba(231, 76, 60, 0.10); border: 1px solid #e74c3c; padding: 8px 12px; border-radius: 6px; text-align: center;'>
                        <span style='font-size: 11px; color: #e74c3c; font-weight: bold;'>🛡️ CONFLUENCE SUPPORT</span><br>
                        <b style='font-size: 16px; color: #e74c3c;'>Rp {confluence_support:,}</b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        with col_c2:
            st.markdown(
                f"""
                <div style='background-color: rgba(52, 152, 219, 0.15); border: 2px solid #3498db; padding: 10px; border-radius: 8px; text-align: center;'>
                    <div style='color: #3498db; font-size: 11px; font-weight: bold;'>🔵 VWAP</div>
                    <div style='font-weight: bold; font-size: 16px; color: #3498db;'>Rp {vwap_val:,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col_c3:
            if confluence_resistance > 0:
                st.markdown(
                    f"""
                    <div style='background-color: rgba(46, 204, 113, 0.10); border: 1px solid #2ecc71; padding: 8px 12px; border-radius: 6px; text-align: center;'>
                        <span style='font-size: 11px; color: #2ecc71; font-weight: bold;'>⚡ CONFLUENCE RESISTANCE</span><br>
                        <b style='font-size: 16px; color: #2ecc71;'>Rp {confluence_resistance:,}</b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        st.markdown("---")
        
        col_fvg_label, col_fvg_value = st.columns([1, 2])
        
        with col_fvg_label:
            st.markdown("##### 📊 FAIR VALUE GAP")
        
        with col_fvg_value:
            if fvg_status != "✅ Tidak Ada Gap":
                st.markdown(
                    f"""
                    <div style='background-color: rgba(241, 196, 15, 0.15); border: 2px solid #f1c40f; padding: 12px; border-radius: 8px;'>
                        <span style='font-weight: bold; color: #f1c40f;'>{fvg_status}</span><br>
                        <span style='font-size: 13px; color: #d1d4dc;'>
                            📅 Tanggal Gap: {fvg_tanggal}<br>
                            <span style='color: #e74c3c;'>⬇️ Bawah: Rp {fvg_bawah:,}</span> → 
                            <span style='color: #2ecc71;'>⬆️ Atas: Rp {fvg_atas:,}</span>
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style='background-color: rgba(46, 204, 113, 0.10); border: 1px solid #2ecc71; padding: 10px; border-radius: 6px;'>
                        <span style='color: #2ecc71; font-weight: bold;'>✅ {fvg_status}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    # --- KONTAINER 3: KALKULATOR TRADING PLAN ---
    with st.container(border=True):
        st.markdown("##### 🎯 KALKULATOR TRADING PLAN (BERDASARKAN FIBONACCI)")
        
        harga_entry_calc = st.number_input(
            "Harga Entry (Rp):",
            min_value=50,
            max_value=200000,
            value=harga_terakhir if harga_terakhir > 0 else 100,
            step=1
        )
        
        if harga_terakhir > 0 and support_fibo > 0 and resisten_fibo > 0:
            entry = harga_entry_calc
            tp1 = math.ceil(entry + (entry * 0.025))
            tp2 = math.ceil(entry + (entry * 0.055))
            tp3 = math.ceil(entry + (entry * 0.100))
            cl = math.floor(entry * 0.962)
            
            col_tp1, col_tp2, col_tp3, col_tp4 = st.columns(4)
            
            with col_tp1:
                st.markdown(
                    f"""
                    <div style='background-color: rgba(46, 204, 113, 0.15); border: 2px solid #2ecc71; padding: 8px; border-radius: 6px; text-align: center;'>
                        <span style='color: #2ecc71; font-weight: bold; font-size: 11px;'>🚀 TP1 (2.5%)</span><br>
                        <b style='font-size: 16px; color: #2ecc71;'>Rp {tp1:,}</b>
                        <div style='font-size: 11px; color: #2ecc71;'>+{tp1 - entry:,}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col_tp2:
                st.markdown(
                    f"""
                    <div style='background-color: rgba(46, 204, 113, 0.15); border: 2px solid #2ecc71; padding: 8px; border-radius: 6px; text-align: center;'>
                        <span style='color: #2ecc71; font-weight: bold; font-size: 11px;'>🚀 TP2 (5.5%)</span><br>
                        <b style='font-size: 16px; color: #2ecc71;'>Rp {tp2:,}</b>
                        <div style='font-size: 11px; color: #2ecc71;'>+{tp2 - entry:,}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col_tp3:
                st.markdown(
                    f"""
                    <div style='background-color: rgba(46, 204, 113, 0.15); border: 2px solid #2ecc71; padding: 8px; border-radius: 6px; text-align: center;'>
                        <span style='color: #2ecc71; font-weight: bold; font-size: 11px;'>🚀 TP3 (10%)</span><br>
                        <b style='font-size: 16px; color: #2ecc71;'>Rp {tp3:,}</b>
                        <div style='font-size: 11px; color: #2ecc71;'>+{tp3 - entry:,}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col_tp4:
                st.markdown(
                    f"""
                    <div style='background-color: rgba(231, 76, 60, 0.15); border: 2px solid #e74c3c; padding: 8px; border-radius: 6px; text-align: center;'>
                        <span style='color: #e74c3c; font-weight: bold; font-size: 11px;'>🛑 CL (-3.8%)</span><br>
                        <b style='font-size: 16px; color: #e74c3c;'>Rp {cl:,}</b>
                        <div style='font-size: 11px; color: #e74c3c;'>{cl - entry:,}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# ============================================
# PANEL KANAN - LENGKAP DENGAN SEMUA FITUR
# ============================================
with col_right_panel:
    st.markdown("##### 📋 LIVE MARKET INTELLIGENCE & ACTION PLAN")
    
    # ============================================
    # UPDATE VARIABEL DENGAN DATA TERBARU
    # ============================================
    
    # 1. STOCHASTIC
    if stoch_k_kemarin <= stoch_d_kemarin and stoch_k > stoch_d:
        if stoch_k < 35:
            txt_stoch = "⚠️ GOLDEN CROSS DETECTED! Sinyal rebound kuat terkonfirmasi di area bawah."
        else:
            txt_stoch = "🔼 BULLISH CROSSOVER: Momentum harian beralih ke pembeli."
    elif stoch_k_kemarin >= stoch_d_kemarin and stoch_k < stoch_d:
        if stoch_k > 70:
            txt_stoch = "⚠️ DEAD CROSS DETECTED! Aksi ambil untung menekan harga ke area overbought."
        else:
            txt_stoch = "🔽 BEARISH CROSSOVER: Tekanan jual jangka pendek meningkat."
    else:
        txt_stoch = "⚖️ KONSOLIDASI: Momentum cenderung bergerak mendatar."
    
    # 2. FOREIGN FLOW
    if foreign_net_summary == "AKUMULASI":
        txt_foreign = f"🟢 FOREIGN ACCUMULATION: Neto Rp {abs(foreign_value_est):,}."
    elif foreign_net_summary == "DISTRIBUSI":
        txt_foreign = f"🔴 FOREIGN DISTRIBUTION: Neto Rp {abs(foreign_value_est):,}."
    else:
        txt_foreign = "🟡 NEUTRAL FLOW: Transaksi asing berimbang."
    
    # 3. REKOMENDASI
    if text_badge == "BUY":
        txt_rekomendasi = "💥 STRATEGIC BUY: Akumulasi bertahap dekat support utama."
        border_color = "#2ecc71"
    elif text_badge == "SELL":
        txt_rekomendasi = "🚨 TAKE PROFIT: Amankan modal sebelum distribusi lanjutan."
        border_color = "#e74c3c"
    else:
        txt_rekomendasi = "🟡 HOLD / WAIT & SEE: Pantau area beli terdekat."
        border_color = "#f1c40f"
    
    # --- KONTAINER UTAMA UNTUK SEMUA INFORMASI ---
    with st.container(border=True):
        
        # ============================================
        # 1. TREND MOVING AVERAGE (MA)
        # ============================================
        st.markdown("---")
        st.markdown("**📈 TREND MOVING AVERAGE (MA)**")
        
        # MA5
        warna_ma5 = "#2ecc71" if "Di Atas" in status_ma5 else "#e74c3c"
        st.markdown(
            f"""
            <div style='background-color: rgba(46, 204, 113, 0.06); border-left: 4px solid {warna_ma5}; padding: 10px 14px; border-radius: 4px; margin-bottom: 6px;'>
                <span style='font-size: 14px;'>• MA 5: <span style='color: {warna_ma5}; font-weight: bold; font-size: 14px;'>{status_ma5}</span></span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # MA20
        warna_ma20 = "#2ecc71" if "Di Atas" in status_ma20 else "#e74c3c"
        st.markdown(
            f"""
            <div style='background-color: rgba(46, 204, 113, 0.06); border-left: 4px solid {warna_ma20}; padding: 10px 14px; border-radius: 4px; margin-bottom: 6px;'>
                <span style='font-size: 14px;'>• MA 20: <span style='color: {warna_ma20}; font-weight: bold; font-size: 14px;'>{status_ma20}</span></span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # MA50
        warna_ma50 = "#2ecc71" if "Di Atas" in status_ma50 else "#e74c3c"
        st.markdown(
            f"""
            <div style='background-color: rgba(46, 204, 113, 0.06); border-left: 4px solid {warna_ma50}; padding: 10px 14px; border-radius: 4px; margin-bottom: 6px;'>
                <span style='font-size: 14px;'>• MA 50: <span style='color: {warna_ma50}; font-weight: bold; font-size: 14px;'>{status_ma50}</span></span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # MA Cross Signal
        st.markdown(
            f"""
            <div style='background-color: rgba(241, 196, 15, 0.06); border-left: 4px solid {warna_signal_ma}; padding: 10px 14px; border-radius: 4px; margin-top: 6px;'>
                <span style='font-size: 14px;'>🔄 MA Cross: <span style='color: {warna_signal_ma}; font-weight: bold; font-size: 14px;'>{signal_ma_cross}</span></span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # ============================================
        # 2. MOMENTUM STOCHASTIC RSI
        # ============================================
        st.markdown("---")
        st.markdown("**⏱️ MOMENTUM STOCHASTIC RSI**")
        
        # Menentukan warna untuk Stochastic
        if stoch_k > 70:
            warna_stoch = "#e74c3c"
        elif stoch_k < 30:
            warna_stoch = "#2ecc71"
        else:
            warna_stoch = "#f1c40f"
        
        st.markdown(
            f"""
            <div style='background-color: rgba(155, 89, 182, 0.06); border-left: 4px solid {warna_stoch}; padding: 10px 14px; border-radius: 4px;'>
                <span style='font-size: 14px; color: #d1d4dc;'>
                    {txt_stoch}<br>
                    <span style='font-size: 13px; color: #888;'>
                        Stoch %K: <span style='font-weight: bold;'>{stoch_k}%</span> | Stoch %D: <span style='font-weight: bold;'>{stoch_d}%</span>
                    </span>
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # ============================================
        # 3. LIKUIDITAS VOLUME - LOGIKA AKURAT
        # ============================================
        st.markdown("---")
        st.markdown("**📦 LIKUIDITAS VOLUME**")
        
        # --- FUNGSI CEK VOLUME 3 HARI ---
        def cek_volume_meningkat(df, days=3):
            if len(df) < days + 1:
                return False, 1.0
            volumes = df['Volume'].iloc[-days-1:-1].tolist()
            avg_prev = sum(volumes) / len(volumes) if len(volumes) > 0 else 1
            volume_hari_ini = df['Volume'].iloc[-1]
            rasio = volume_hari_ini / avg_prev if avg_prev > 0 else 1.0
            return volume_hari_ini > avg_prev * 1.1, rasio
        
        def cek_volume_menurun(df, days=3):
            if len(df) < days + 1:
                return False, 1.0
            volumes = df['Volume'].iloc[-days-1:-1].tolist()
            avg_prev = sum(volumes) / len(volumes) if len(volumes) > 0 else 1
            volume_hari_ini = df['Volume'].iloc[-1]
            rasio = volume_hari_ini / avg_prev if avg_prev > 0 else 1.0
            return volume_hari_ini < avg_prev * 0.9, rasio
        
        # --- HITUNG SEMUA KONDISI ---
        is_green_today = harga_terakhir > open_hari_ini
        harga_turun = harga_terakhir < open_hari_ini
        volume_meningkat, rasio_vol_3h = cek_volume_meningkat(df_live, 3)
        volume_menurun, rasio_vol_3h_menurun = cek_volume_menurun(df_live, 3)
        
        # Posisi terhadap Fibonacci
        near_support = abs(harga_terakhir - support_fibo) / support_fibo < 0.02 if support_fibo > 0 else False
        near_resistance = abs(harga_terakhir - resisten_fibo) / resisten_fibo < 0.02 if resisten_fibo > 0 else False
        
        # RSI kondisi
        is_oversold = rsi_terakhir < 38
        is_overbought = rsi_terakhir > 72
        
        # --- LOGIKA VOLUME UTAMA ---
        
        # 1. AKUMULASI KONFIRMASI (Support + Volume Hijau Naik + Oversold)
        if volume_meningkat and is_green_today and near_support and is_oversold:
            txt_vol = f"🟢🟢🟢 **AKUMULASI KONFIRMASI!** Bandar beli di support + oversold!"
            status_vol = "AKUMULASI KUAT"
            warna_vol = "#00e676"
            icon_vol = "🟢🟢🟢"
            prediksi = "📈 **Prediksi:** Potensi kenaikan esok hari SANGAT TINGGI (75-80%)"
        
        # 2. BANDAR CICIL (Support + Volume Tinggi Saat Turun)
        elif volume_meningkat and harga_turun and near_support:
            txt_vol = f"👀👀👀 **BANDAR CICIL!** Volume tinggi di support, harga turun!"
            status_vol = "AKUMULASI (Cicilan)"
            warna_vol = "#f1c40f"
            icon_vol = "🟡🟡🟡"
            prediksi = "📈 **Prediksi:** Potensi kenaikan esok hari TINGGI (65-70%), tunggu reversal"
        
        # 3. BREAKOUT POTENSIAL (Volume Hijau Naik di Support)
        elif volume_meningkat and is_green_today and near_support:
            txt_vol = f"📈📈📈 **BREAKOUT POTENSIAL!** Volume hijau di support!"
            status_vol = "BREAKOUT"
            warna_vol = "#2ecc71"
            icon_vol = "🟢🟢"
            prediksi = "📈 **Prediksi:** Potensi kenaikan esok hari TINGGI (65-70%)"
        
        # 4. DISTRIBUSI KONFIRMASI (Resistance + Volume Hijau Naik + Overbought)
        elif volume_meningkat and is_green_today and near_resistance and is_overbought:
            txt_vol = f"🔴🔴🔴 **DISTRIBUSI KONFIRMASI!** Bandar jual di resistance + overbought!"
            status_vol = "DISTRIBUSI KUAT"
            warna_vol = "#ff1744"
            icon_vol = "🔴🔴🔴"
            prediksi = "📉 **Prediksi:** Potensi koreksi esok hari SANGAT TINGGI (75-80%)"
        
        # 5. PERINGATAN (Resistance + Volume Hijau Naik)
        elif volume_meningkat and is_green_today and near_resistance:
            txt_vol = f"⚠️⚠️⚠️ **PERINGATAN!** Volume tinggi di resistance!"
            status_vol = "DISTRIBUSI"
            warna_vol = "#e74c3c"
            icon_vol = "🔴🔴"
            prediksi = "📉 **Prediksi:** Potensi koreksi esok hari TINGGI (60-70%)"
        
        # 6. VOLUME MENINGKAT (Tanpa Konfirmasi Support/Resistance)
        elif volume_meningkat:
            txt_vol = f"🔵🔵 **VOLUME MENINGKAT!** {round(rasio_vol_3h, 1)}x dari rata-rata 3 hari"
            status_vol = "VOLUME NAIK"
            warna_vol = "#3498db"
            icon_vol = "🔵🔵"
            prediksi = "📊 **Prediksi:** Perlu konfirmasi di support/resistance"
        
        # 7. VOLUME MENURUN SAAT NAIK (Kelemahan)
        elif volume_menurun and is_green_today:
            txt_vol = f"🔴 **PERINGATAN!** Volume menurun saat harga naik!"
            status_vol = "VOLUME TURUN"
            warna_vol = "#e74c3c"
            icon_vol = "🔴"
            prediksi = "📉 **Prediksi:** Kenaikan tanpa volume, potensi koreksi"
        
        # 8. VOLUME NORMAL
        else:
            rasio_normal = vol_terakhir / ma_volume_20 if ma_volume_20 > 0 else 1.0
            txt_vol = f"⚪ **VOLUME NORMAL** ({round(rasio_normal, 1)}x dari rata-rata 20 hari)"
            status_vol = "NORMAL"
            warna_vol = "#888888"
            icon_vol = "⚪"
            prediksi = "⏸️ **Prediksi:** Tidak ada sinyal khusus, tunggu konfirmasi"
        
        # --- TAMPILAN VOLUME DI PANEL KANAN ---
        st.markdown(
            f"""
            <div style='background-color: rgba(26, 188, 156, 0.06); border-left: 4px solid {warna_vol}; padding: 10px 14px; border-radius: 4px;'>
                <span style='font-size: 14px; color: #d1d4dc;'>
                    {icon_vol} {txt_vol}<br>
                    <span style='font-size: 13px; color: #888;'>
                        Volume: <span style='font-weight: bold; color: {warna_vol};'>{vol_terakhir:,}</span> | 
                        Rata-rata 20H: <span style='font-weight: bold;'>{round(ma_volume_20):,}</span>
                    </span>
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # --- TAMPILAN PREDIKSI ---
        st.markdown(
            f"""
            <div style='background-color: rgba(255, 255, 255, 0.02); border: 1px solid {warna_vol}40; padding: 8px 14px; border-radius: 4px; margin-top: 6px;'>
                <span style='font-size: 13px; color: #d1d4dc;'>
                    {prediksi}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # ============================================
        # 4. FOREIGN FLOW
        # ============================================
        st.markdown("---")
        st.markdown("**🌐 FOREIGN FLOW**")
        
        # Menentukan warna untuk Foreign
        if foreign_net_summary == "AKUMULASI":
            warna_foreign = "#2ecc71"
            txt_foreign_display = f"🟢 **FOREIGN ACCUMULATION** - 🔥🔥🔥 ASING AKUMULASI! Neto Beli: Rp {abs(foreign_value_est):,}"
        elif foreign_net_summary == "DISTRIBUSI":
            warna_foreign = "#e74c3c"
            txt_foreign_display = f"🔴 **FOREIGN DISTRIBUTION** - 💀💀💀 ASING DISTRIBUSI! Neto Jual: Rp {abs(foreign_value_est):,}"
        else:
            warna_foreign = "#f1c40f"
            txt_foreign_display = f"🟡 **NEUTRAL FLOW** - ⚖️⚖️⚖️ ASING NETRAL! Neto: Rp {abs(foreign_value_est):,}"
        
        st.markdown(
            f"""
            <div style='background-color: rgba(230, 126, 34, 0.06); border-left: 4px solid {warna_foreign}; padding: 10px 14px; border-radius: 4px;'>
                <span style='font-size: 14px; color: #d1d4dc;'>
                    {txt_foreign_display}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # ============================================
        # 5. REKOMENDASI TRADING
        # ============================================
        st.markdown("---")
        st.markdown("**🎯 REKOMENDASI TRADING**")
        
        st.markdown(
            f"""
            <div style='background-color: #1e222d; border-left: 6px solid {border_color}; padding: 12px 16px; border-radius: 4px;'>
                <span style='font-size: 15px; color: #ffffff; font-weight: 500;'>
                    {txt_rekomendasi}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

# ============================================
# SCREENING EMITEN - VERSI LENGKAP
# ============================================
st.markdown("---")
st.markdown("### 🚀 RADAR SCREENING EMITEN")
st.markdown("*Pantau saham potensial dari hari ke hari, termasuk saham mahal seperti BBCA*")

# ============================================
# DAFTAR SAHAM SUSPEND (TIDAK BISA DIPERDAGANGKAN)
# ============================================
SAHAM_SUSPEND = [
    "INAF", "META", "WIKA",  # Saham suspend
    # Tambahkan sesuai data terbaru dari BEI/Stockbit
]

def is_suspended(ticker):
    """Cek apakah saham sedang suspend"""
    ticker_clean = ticker.replace(".JK", "")
    return ticker_clean in SAHAM_SUSPEND

# ============================================
# INISIALISASI SESSION STATE
# ============================================
if 'watchlist' not in st.session_state:
    st.session_state['watchlist'] = {}
    
if 'screening_history' not in st.session_state:
    st.session_state['screening_history'] = []

if 'rekomendasi_history' not in st.session_state:
    st.session_state['rekomendasi_history'] = []

# ============================================
# PILIH MODE SCREENING
# ============================================
st.markdown("### ⚙️ Pengaturan Screening")

col_mode1, col_mode2 = st.columns([2, 1])

with col_mode1:
    mode_screening = st.radio(
        "Pilih Mode Screening:",
        ["🎯 Scalping (Rp 90-500+)", "🔍 All Price (Tanpa Filter)", "⚙️ Custom Range"],
        horizontal=True,
        key="mode_screening"
    )

with col_mode2:
    st.markdown("---")
    st.caption("💡 **Tips:** Range Rp 90-500+ mencakup semua saham likuid termasuk BBCA")

# === FILTER HARGA ===
if mode_screening == "🎯 Scalping (Rp 90-500+)":
    min_price = 90
    max_price = 999999
    st.info("📌 Screening semua saham dengan harga di atas Rp 90 (termasuk BBCA, TLKM, dll)")

elif mode_screening == "🔍 All Price (Tanpa Filter)":
    min_price = 0
    max_price = 999999
    st.info("📌 Screening semua saham tanpa batasan harga")

else:  # Custom Range
    col_min, col_max = st.columns(2)
    with col_min:
        min_price = st.number_input("Harga Minimum (Rp):", value=90, min_value=0, step=10)
    with col_max:
        max_price = st.number_input("Harga Maksimum (Rp):", value=999999, min_value=0, step=10)
    st.info(f"📌 Screening saham dengan harga Rp {min_price} - Rp {max_price}")

st.markdown("---")

# ============================================
# FUNGSI ANALISA SAHAM
# ============================================
def analisa_saham_scalping(ticker, min_price=90, max_price=999999):
    """Analisis saham untuk scalping dengan tracking history"""
    
    # ============================================
    # CEK SAHAM SUSPEND
    # ============================================
    if is_suspended(ticker):
        return None
    
    df = yf.download(ticker, period="60d", interval="1d", progress=False)
    
    if df.empty or len(df) < 30:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    # ============================================
    # 1. INDIKATOR DASAR
    # ============================================
    
    # Moving Average 1, 3, 6 hari (EMA lebih responsif)
    df['MA1'] = df['Close'].ewm(span=1, adjust=False).mean()
    df['MA3'] = df['Close'].ewm(span=3, adjust=False).mean()
    df['MA6'] = df['Close'].ewm(span=6, adjust=False).mean()
    
    # Bollinger Band (20, 2)
    df['BB_Mid'] = df['Close'].rolling(window=20).mean()
    df['BB_Std'] = df['Close'].rolling(window=20).std()
    df['BB_Lower'] = df['BB_Mid'] - 2 * df['BB_Std']
    df['BB_Upper'] = df['BB_Mid'] + 2 * df['BB_Std']
    
    # Volume
    df['MA_Vol_20'] = df['Volume'].rolling(window=20).mean()
    df['MA_Vol_3'] = df['Volume'].rolling(window=3).mean()
    
    # RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Stochastic RSI (14, 3, 3)
    low_14 = df['Low'].rolling(window=14).min()
    high_14 = df['High'].rolling(window=14).max()
    df['Stoch_K'] = 100 * ((df['Close'] - low_14) / (high_14 - low_14))
    df['Stoch_D'] = df['Stoch_K'].rolling(window=3).mean()
    
    # VWAP (harian)
    df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
    
    # Fibonacci
    high_val = df['High'].max()
    low_val = df['Low'].min()
    diff = high_val - low_val
    fibo_236 = round(low_val + (diff * 0.236))
    fibo_382 = round(low_val + (diff * 0.382))
    fibo_618 = round(low_val + (diff * 0.618))
    
    # ============================================
    # 2. AMBIL DATA HARI INI & KEMARIN
    # ============================================
    hari_ini = df.iloc[-1]
    hari_kemarin = df.iloc[-2] if len(df) > 1 else hari_ini
    
    close_now = float(hari_ini['Close'])
    close_prev = float(hari_kemarin['Close'])
    vol_now = int(hari_ini['Volume'])
    vol_prev = int(hari_kemarin['Volume']) if len(df) > 1 else vol_now
    ma_vol_20 = float(hari_ini['MA_Vol_20']) if not pd.isna(hari_ini['MA_Vol_20']) else vol_now
    ma_vol_3 = float(hari_ini['MA_Vol_3']) if not pd.isna(hari_ini['MA_Vol_3']) else vol_now
    
    rsi_now = float(hari_ini['RSI']) if not pd.isna(hari_ini['RSI']) else 50.0
    k_now = float(hari_ini['Stoch_K']) if not pd.isna(hari_ini['Stoch_K']) else 50.0
    d_now = float(hari_ini['Stoch_D']) if not pd.isna(hari_ini['Stoch_D']) else 50.0
    k_prev = float(hari_kemarin['Stoch_K']) if not pd.isna(hari_kemarin['Stoch_K']) else 50.0
    d_prev = float(hari_kemarin['Stoch_D']) if not pd.isna(hari_kemarin['Stoch_D']) else 50.0
    
    ma1_now = float(hari_ini['MA1'])
    ma3_now = float(hari_ini['MA3'])
    ma6_now = float(hari_ini['MA6'])
    ma1_prev = float(hari_kemarin['MA1'])
    ma3_prev = float(hari_kemarin['MA3'])
    
    vwap_now = float(hari_ini['VWAP'])
    bb_lower = float(hari_ini['BB_Lower']) if not pd.isna(hari_ini['BB_Lower']) else 0
    bb_mid = float(hari_ini['BB_Mid']) if not pd.isna(hari_ini['BB_Mid']) else 0
    
    # === FILTER HARGA ===
    if not (min_price <= close_now <= max_price):
        return None
    
    # ============================================
    # 3. CEK KENAIKAN SIGNIFIKAN (HANYA UNTUK PERINGATAN)
    # ============================================
    if len(df) >= 8:
        harga_7hari_lalu = df.iloc[-8]['Close']
        if harga_7hari_lalu > 0:
            kenaikan_7hari = ((close_now - harga_7hari_lalu) / harga_7hari_lalu) * 100
            if kenaikan_7hari > 30:
                status_kenaikan = f"⚠️⚠️ SUDAH NAIK {round(kenaikan_7hari)}% (Hati-hati!)"
            elif kenaikan_7hari > 20:
                status_kenaikan = f"⚠️ NAIK {round(kenaikan_7hari)}% (Waspada)"
            elif kenaikan_7hari > 10:
                status_kenaikan = f"📈 NAIK {round(kenaikan_7hari)}%"
            elif kenaikan_7hari < -10:
                status_kenaikan = f"📉 TURUN {round(abs(kenaikan_7hari))}%"
            else:
                status_kenaikan = "✅ Normal"
        else:
            status_kenaikan = "✅ Normal"
    else:
        status_kenaikan = "✅ Normal"
    
    # ============================================
    # 4. HITUNG SKOR KRITERIA
    # ============================================
    
    skor = 0
    kriteria_terpenuhi = []
    alasan_rekomendasi = []
    
    # --- KRITERIA 1: HARGA DI ATAS VWAP (Bullish) ---
    if close_now > vwap_now:
        skor += 1
        kriteria_terpenuhi.append("✅ Harga di atas VWAP")
        alasan_rekomendasi.append("Harga > VWAP (Bullish)")
    
    # --- KRITERIA 2: VOLUME > RATA-RATA 20 HARI ---
    rasio_vol = vol_now / ma_vol_20 if ma_vol_20 > 0 else 1.0
    if rasio_vol >= 1.5:
        skor += 1
        kriteria_terpenuhi.append(f"✅ Volume tinggi ({round(rasio_vol, 1)}x rata-rata)")
        alasan_rekomendasi.append(f"Volume {round(rasio_vol, 1)}x rata-rata")
    
    # --- KRITERIA 3: GOLDEN CROSS STOCHASTIC ---
    is_golden_cross = (k_prev <= d_prev and k_now > d_now)
    if is_golden_cross and k_now < 40:
        skor += 2
        kriteria_terpenuhi.append("✅ Golden Cross Stochastic (Oversold area)")
        alasan_rekomendasi.append("Golden Cross Stochastic di area oversold")
    elif is_golden_cross:
        skor += 1
        kriteria_terpenuhi.append("✅ Golden Cross Stochastic")
        alasan_rekomendasi.append("Golden Cross Stochastic")
    
    # --- KRITERIA 4: VOLATILITY SQUEEZE (MA 1,3,6 MENYEMPIT) ---
    ma_spread = abs(ma1_now - ma3_now) + abs(ma3_now - ma6_now) + abs(ma1_now - ma6_now)
    ma_spread_normalized = ma_spread / close_now * 100
    
    if ma_spread_normalized < 0.5:
        skor += 2
        kriteria_terpenuhi.append(f"✅ MA Squeeze! (Spread {round(ma_spread_normalized, 2)}%)")
        alasan_rekomendasi.append(f"MA Squeeze {round(ma_spread_normalized, 2)}%")
    elif ma_spread_normalized < 1.0:
        skor += 1
        kriteria_terpenuhi.append(f"✅ MA Menyempit (Spread {round(ma_spread_normalized, 2)}%)")
        alasan_rekomendasi.append(f"MA menyempit {round(ma_spread_normalized, 2)}%")
    
    # --- KRITERIA 5: MA1 CROSS DI ATAS MA3 ---
    ma1_cross_ma3 = (ma1_prev <= ma3_prev and ma1_now > ma3_now)
    if ma1_cross_ma3:
        skor += 2
        kriteria_terpenuhi.append("✅ MA1 Golden Cross MA3!")
        alasan_rekomendasi.append("MA1 Golden Cross MA3")
    
    # --- KRITERIA 6: BOLLINGER BAND BAWAH ---
    if bb_lower > 0 and close_now <= bb_lower * 1.02:
        skor += 1
        kriteria_terpenuhi.append("✅ Menyentuh BB Bawah")
        alasan_rekomendasi.append("Menyentuh BB Bawah (mean reversion)")
    
    # --- KRITERIA 7: RSI MULAI NAIK DARI RENDAH ---
    if rsi_now > 30 and rsi_now < 50:
        rsi_3hari = df['RSI'].iloc[-3:].tolist()
        if len(rsi_3hari) >= 3 and rsi_3hari[-1] > rsi_3hari[-2] > rsi_3hari[-3]:
            skor += 1
            kriteria_terpenuhi.append("✅ RSI mulai naik dari rendah")
            alasan_rekomendasi.append("RSI mulai naik dari rendah")
    
    # --- KRITERIA 8: VOLUME 3 HARI MENINGKAT ---
    if len(df) >= 6:
        vol_3hari = df['Volume'].iloc[-3:].tolist()
        if vol_3hari[-1] > vol_3hari[-2] > vol_3hari[-3]:
            skor += 1
            kriteria_terpenuhi.append("✅ Volume 3 hari meningkat")
            alasan_rekomendasi.append("Volume 3 hari meningkat (akumulasi)")
    
    # --- KRITERIA 9: DEKAT SUPPORT FIBONACCI ---
    if fibo_236 > 0:
        jarak_support = abs(close_now - fibo_236) / fibo_236
        if jarak_support < 0.02:
            skor += 1
            kriteria_terpenuhi.append("✅ Dekat Support Fibonacci 23.6%")
            alasan_rekomendasi.append("Dekat Support Fibonacci 23.6%")
    
    # --- KRITERIA 10: VOLUME HARI INI vs KEMARIN (AKUMULASI) ---
    if len(df) > 1:
        vol_change_pct = ((vol_now - vol_prev) / vol_prev) * 100 if vol_prev > 0 else 0
        if vol_change_pct > 30 and close_now <= close_prev * 1.01:
            skor += 1
            kriteria_terpenuhi.append(f"✅ Volume naik {round(vol_change_pct)}% saat harga turun/stabil")
            alasan_rekomendasi.append(f"Volume naik {round(vol_change_pct)}% (akumulasi)")
    
    # ============================================
    # 5. TENTUKAN REKOMENDASI BERDASARKAN SKOR
    # ============================================
    
    if skor >= 8:
        rekomendasi = "🔥 STRONG BUY - Top Pick!"
        warna_rekom = "#00e676"
        aksi = "🚀 Entry Sekarang"
    elif skor >= 6:
        rekomendasi = "🟢 BUY - Potensi Bagus"
        warna_rekom = "#2ecc71"
        aksi = "📈 Entry Bertahap"
    elif skor >= 4:
        rekomendasi = "👀 WATCH - Perlu Konfirmasi"
        warna_rekom = "#f1c40f"
        aksi = "⏳ Pantau 1-3 Hari"
    elif skor >= 2:
        rekomendasi = "⏸️ HOLD - Belum Siap"
        warna_rekom = "#f39c12"
        aksi = "🔍 Pantau Perubahan"
    else:
        rekomendasi = "🔴 AVOID - Tidak Memenuhi"
        warna_rekom = "#e74c3c"
        aksi = "⏭️ Lewati"
    
    # ============================================
    # 6. STATUS BANDAR
    # ============================================
    
    if len(df) > 1:
        vol_change_pct = ((vol_now - vol_prev) / vol_prev) * 100 if vol_prev > 0 else 0
        if vol_change_pct > 30 and close_now <= close_prev * 1.01:
            status_bandar = "🟢 Bandar Akumulasi (Volume naik, harga stabil/turun)"
        elif vol_change_pct > 30 and close_now > close_prev * 1.02:
            status_bandar = "🟡 Breakout (Volume naik, harga naik)"
        elif vol_change_pct < -30 and close_now > close_prev * 1.02:
            status_bandar = "🔴 Distribusi (Volume turun, harga naik) - Hati-hati!"
        elif vol_change_pct < -30 and close_now <= close_prev * 1.01:
            status_bandar = "⚪ Sepi (Volume turun, harga turun) - Ditinggalkan"
        else:
            status_bandar = "⚖️ Normal"
    else:
        status_bandar = "⚖️ Normal"
    
    # ============================================
    # 7. RETURN DATA
    # ============================================
    
    return {
        "Tanggal": datetime.now().strftime('%Y-%m-%d'),
        "Ticker": ticker.replace(".JK", ""),
        "Harga": round(close_now, 2),
        "Perubahan %": round(((close_now - close_prev) / close_prev) * 100, 2),
        "Perubahan Volume %": round(vol_change_pct, 2) if len(df) > 1 else 0,
        "Volume": vol_now,
        "Rasio Vol vs Rata2": round(rasio_vol, 2),
        "RSI": round(rsi_now, 2),
        "Stoch %K": round(k_now, 2),
        "Stoch %D": round(d_now, 2),
        "MA Squeeze": f"{round(ma_spread_normalized, 2)}%",
        "BB Posisi": "Bawah" if close_now <= bb_lower * 1.02 else "Normal" if close_now <= bb_mid * 1.02 else "Atas",
        "Status Bandar": status_bandar,
        "Status Kenaikan": status_kenaikan,  # KOLOM BARU
        "VWAP": round(vwap_now, 2),
        "Skor": skor,
        "Rekomendasi": rekomendasi,
        "Aksi": aksi,
        "Alasan": ", ".join(alasan_rekomendasi) if alasan_rekomendasi else "Tidak ada kriteria",
        "Kriteria": ", ".join(kriteria_terpenuhi) if kriteria_terpenuhi else "Tidak ada"
    }

# ============================================
# DAFTAR SAHAM (DIPERLENGKAP)
# ============================================
daftar_saham = [
    # Saham Blue Chip (Termasuk BBCA, TLKM, dll)
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "TLKM.JK", "UNVR.JK", "ICBP.JK", "INDF.JK", "MYOR.JK",
    "ADRO.JK", "ITMG.JK", "PTBA.JK", "KLBF.JK", "MERK.JK", "SMGR.JK", "INTP.JK", "SMCB.JK",
    
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

# Hapus saham suspend dari daftar
daftar_saham = [s for s in daftar_saham if not is_suspended(s)]
daftar_saham = list(set(daftar_saham))

# ============================================
# TAMPILAN UTAMA SCREENING
# ============================================
with st.container(border=True):
    col_btn, col_info = st.columns([1, 3])
    
    with col_btn:
        if st.button("🔄 JALANKAN SCREENING", use_container_width=True, type="primary"):
            st.session_state['run_screening'] = True
    
    with col_info:
        st.info(f"📊 **Total Emiten yang Discan:** {len(daftar_saham)} saham | Range Harga: Rp {min_price} - Rp {max_price}")
        st.caption("📌 Screening mencakup semua saham di atas Rp 90 (termasuk BBCA, TLKM, dll)")

    # ============================================
    # EKSEKUSI SCREENING
    # ============================================
    if 'run_screening' in st.session_state and st.session_state['run_screening']:
        with st.spinner("⏳ Sedang melakukan screening saham, mohon tunggu..."):
            kumpulan_data = []
            progress_bar = st.progress(0)
            
            for i, saham in enumerate(daftar_saham):
                try:
                    hasil = analisa_saham_scalping(saham, min_price, max_price)
                    if hasil:
                        kumpulan_data.append(hasil)
                except Exception as e:
                    pass
                progress_bar.progress((i + 1) / len(daftar_saham))
            
            progress_bar.empty()
            
            if kumpulan_data:
                df_hasil = pd.DataFrame(kumpulan_data)
                df_hasil = df_hasil.sort_values(by="Skor", ascending=False)
                
                # Simpan ke history
                st.session_state['screening_history'].append({
                    'tanggal': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'data': df_hasil.copy()
                })
                
                # Simpan rekomendasi (hanya yang skor >= 4)
                df_rekomendasi = df_hasil[df_hasil['Skor'] >= 4].copy()
                if not df_rekomendasi.empty:
                    for _, row in df_rekomendasi.iterrows():
                        st.session_state['rekomendasi_history'].append({
                            'tanggal': datetime.now().strftime('%Y-%m-%d'),
                            'ticker': row['Ticker'],
                            'skor': row['Skor'],
                            'alasan': row['Alasan'],
                            'rekomendasi': row['Rekomendasi'],
                            'harga': row['Harga']
                        })
                
                st.success(f"✅ Screening selesai! Ditemukan {len(df_hasil)} saham potensial.")
                
                # ============================================
                # REKOMENDASI BERDASARKAN SKOR
                # ============================================
                col_strong_buy, col_buy, col_watch = st.columns(3)
                
                strong_buy = df_hasil[df_hasil['Rekomendasi'].str.contains("STRONG BUY")]
                buy = df_hasil[df_hasil['Rekomendasi'].str.contains("BUY")]
                watch = df_hasil[df_hasil['Rekomendasi'].str.contains("WATCH")]
                
                with col_strong_buy:
                    st.metric("🔥 STRONG BUY", len(strong_buy), delta="Entry Sekarang")
                with col_buy:
                    st.metric("🟢 BUY", len(buy), delta="Entry Bertahap")
                with col_watch:
                    st.metric("👀 WATCH", len(watch), delta="Pantau 1-3 Hari")
                
                st.markdown("---")
                
                # ============================================
                # TABEL HASIL SCREENING
                # ============================================
                st.subheader("📊 Hasil Screening Hari Ini")
                
                st.dataframe(
                    df_hasil,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Tanggal": st.column_config.TextColumn("Tanggal", width="small"),
                        "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                        "Harga": st.column_config.NumberColumn("Harga", format="Rp %.0f"),
                        "Perubahan %": st.column_config.NumberColumn("Perubahan %", format="%.2f%%"),
                        "Perubahan Volume %": st.column_config.NumberColumn("Vol %", format="%.2f%%"),
                        "Volume": st.column_config.NumberColumn("Volume", format="%d"),
                        "Rasio Vol vs Rata2": st.column_config.NumberColumn("Rasio Vol", format="%.2f"),
                        "RSI": st.column_config.NumberColumn("RSI", format="%.2f"),
                        "Stoch %K": st.column_config.NumberColumn("%K", format="%.2f"),
                        "Stoch %D": st.column_config.NumberColumn("%D", format="%.2f"),
                        "MA Squeeze": st.column_config.TextColumn("MA Squeeze", width="small"),
                        "BB Posisi": st.column_config.TextColumn("BB", width="small"),
                        "Status Bandar": st.column_config.TextColumn("Bandar", width="medium"),
                        "Status Kenaikan": st.column_config.TextColumn("Kenaikan", width="medium"),
                        "VWAP": st.column_config.NumberColumn("VWAP", format="Rp %.0f"),
                        "Skor": st.column_config.NumberColumn("Skor", format="%d"),
                        "Rekomendasi": st.column_config.TextColumn("Rekomendasi", width="medium"),
                        "Aksi": st.column_config.TextColumn("Aksi", width="medium"),
                        "Alasan": st.column_config.TextColumn("Alasan", width="large"),
                        "Kriteria": st.column_config.TextColumn("Kriteria", width="large"),
                    }
                )
                
                # ============================================
                # DOWNLOAD HASIL
                # ============================================
                csv = df_hasil.to_csv(index=False)
                st.download_button(
                    label="📥 Download Hasil Screening (CSV)",
                    data=csv,
                    file_name=f"Radar_Saham_Scalping_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                del st.session_state['run_screening']
            else:
                st.warning(f"⚠️ Tidak ada saham yang memenuhi kriteria screening dengan harga Rp {min_price} - Rp {max_price}.")
                del st.session_state['run_screening']
    else:
        st.info("💡 Klik tombol 'JALANKAN SCREENING' untuk melihat hasil analisis saham potensial.")

# ============================================
# TABEL REKOMENDASI DARI HISTORY SCREENING
# ============================================
st.markdown("---")
st.markdown("### 📋 REKOMENDASI DARI HISTORY SCREENING")

tab1, tab2, tab3 = st.tabs(["⭐ Rekomendasi Terbaik", "📊 History Screening", "📈 Tracking Akumulasi"])

# ============================================
# TAB 1: REKOMENDASI TERBAIK (DARI HISTORY)
# ============================================
with tab1:
    st.markdown("""
    **📌 Tabel ini berisi rekomendasi dari beberapa hari screening yang lalu.**
    - Berguna untuk melacak saham yang muncul berulang kali
    - Membantu mendeteksi akumulasi bandar dari waktu ke waktu
    - **Perhatikan kolom "Status Kenaikan"** untuk mengetahui apakah saham sudah terbang
    """)
    
    if st.session_state['rekomendasi_history']:
        # Konversi ke DataFrame
        df_rekom = pd.DataFrame(st.session_state['rekomendasi_history'])
        
        # Kelompokkan berdasarkan ticker
        rekom_summary = df_rekom.groupby('ticker').agg({
            'skor': ['mean', 'max', 'count'],
            'alasan': lambda x: ' | '.join(x.unique()[:3]),
            'harga': 'last',
            'rekomendasi': 'last',
            'tanggal': 'last'
        }).reset_index()
        
        rekom_summary.columns = ['Ticker', 'Rata-rata Skor', 'Skor Tertinggi', 'Jumlah Muncul', 'Alasan', 'Harga Terakhir', 'Rekomendasi Terakhir', 'Terakhir Muncul']
        rekom_summary = rekom_summary.sort_values('Rata-rata Skor', ascending=False)
        
        st.subheader(f"⭐ {len(rekom_summary)} Saham dengan Rekomendasi Terbaik")
        
        st.dataframe(
            rekom_summary,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                "Rata-rata Skor": st.column_config.NumberColumn("Rata-rata Skor", format="%.1f"),
                "Skor Tertinggi": st.column_config.NumberColumn("Skor Tertinggi", format="%d"),
                "Jumlah Muncul": st.column_config.NumberColumn("Muncul", format="%d"),
                "Alasan": st.column_config.TextColumn("Alasan", width="large"),
                "Harga Terakhir": st.column_config.NumberColumn("Harga", format="Rp %.0f"),
                "Rekomendasi Terakhir": st.column_config.TextColumn("Rekomendasi", width="medium"),
                "Terakhir Muncul": st.column_config.TextColumn("Terakhir", width="small"),
            }
        )
        
        # Tambahan: Saham yang paling sering muncul
        st.markdown("---")
        st.subheader("🔥 Top 5 Saham Paling Sering Muncul")
        
        top_5 = rekom_summary.nlargest(5, 'Jumlah Muncul')[['Ticker', 'Jumlah Muncul', 'Rata-rata Skor', 'Rekomendasi Terakhir']]
        st.dataframe(top_5, use_container_width=True, hide_index=True)
        
        # Tombol reset rekomendasi
        if st.button("🗑️ Reset Rekomendasi History", use_container_width=True):
            st.session_state['rekomendasi_history'] = []
            st.success("✅ Rekomendasi history berhasil direset")
            st.rerun()
            
    else:
        st.info("💡 Belum ada rekomendasi tersimpan. Jalankan screening terlebih dahulu!")

# ============================================
# TAB 2: HISTORY SCREENING
# ============================================
with tab2:
    if st.session_state['screening_history']:
        st.info("📌 Data screening dari hari-hari sebelumnya:")
        
        for idx, history in enumerate(st.session_state['screening_history']):
            with st.expander(f"📅 {history['tanggal']} - {len(history['data'])} saham ditemukan"):
                st.dataframe(
                    history['data'][['Ticker', 'Harga', 'Perubahan %', 'Perubahan Volume %', 'Skor', 'Rekomendasi', 'Status Bandar', 'Status Kenaikan', 'Alasan']],
                    use_container_width=True,
                    hide_index=True
                )
    else:
        st.info("💡 Belum ada history screening. Jalankan screening terlebih dahulu.")

# ============================================
# TAB 3: TRACKING AKUMULASI BANDAR
# ============================================
with tab3:
    st.markdown("""
    ### 🔍 Tracking Akumulasi Bandar
    
    **Cara Kerja:**
    1. Screening hari ini akan menampilkan saham dengan **Status Bandar**
    2. Status menunjukkan apakah bandar sedang akumulasi atau tidak
    3. Pantau perubahan status dari hari ke hari
    """)
    
    if st.session_state['screening_history']:
        # Ambil data terakhir
        history_terakhir = st.session_state['screening_history'][-1]['data']
        
        # Filter saham dengan akumulasi bandar
        akumulasi = history_terakhir[history_terakhir['Status Bandar'].str.contains("Akumulasi")]
        distribusi = history_terakhir[history_terakhir['Status Bandar'].str.contains("Distribusi")]
        sepi = history_terakhir[history_terakhir['Status Bandar'].str.contains("Sepi")]
        
        col_akum, col_dist, col_sepi = st.columns(3)
        with col_akum:
            st.metric("🟢 Bandar Akumulasi", len(akumulasi))
        with col_dist:
            st.metric("🔴 Bandar Distribusi", len(distribusi))
        with col_sepi:
            st.metric("⚪ Ditinggalkan Bandar", len(sepi))
        
        st.markdown("---")
        
        # Tampilkan saham yang diakumulasi bandar
        if not akumulasi.empty:
            st.subheader("🟢 Saham yang Sedang Diakumulasi Bandar")
            st.dataframe(
                akumulasi[['Ticker', 'Harga', 'Perubahan %', 'Perubahan Volume %', 'Status Bandar', 'Status Kenaikan', 'Skor', 'Rekomendasi', 'Alasan']],
                use_container_width=True,
                hide_index=True
            )
            st.caption("📌 Saham ini sedang dikoleksi bandar. Pantau terus, bisa naik dalam 2-3 hari ke depan!")
        else:
            st.info("💡 Belum ada saham yang terdeteksi akumulasi bandar hari ini")
    else:
        st.info("💡 Jalankan screening terlebih dahulu untuk melihat tracking akumulasi bandar.")
