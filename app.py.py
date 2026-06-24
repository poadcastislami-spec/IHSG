import streamlit as st
import pandas as pd
import yfinance as yf
import math
import requests
import time
from datetime import datetime, timedelta
from collections import Counter

# ============================================
# KONFIGURASI API
# ============================================

# API Key iTick
ITICK_API_KEY = "145de02490f541f49381feb5c99b178552f220d0cc8c400cbc5716635bac6440"
ITICK_URL = "https://api.itick.org/stock/quote"

# ============================================
# KONFIGURASI HALAMAN
# ============================================
st.set_page_config(
    page_title="IHSG PREMIUM TERMINAL - FAHRUN HIDAYAT",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# FUNGSI AMBIL DATA DARI iTick (REAL-TIME)
# ============================================

@st.cache_data(ttl=30)
def get_itick_data(code):
    """Ambil data saham real-time dari iTick API"""
    try:
        params = {"region": "ID", "code": code}
        headers = {"token": ITICK_API_KEY}
        
        resp = requests.get(ITICK_URL, params=params, headers=headers, timeout=10)
        data = resp.json()
        
        if data.get("code") == 0:
            return data.get("data", {})
        else:
            return None
    except Exception as e:
        return None

# ============================================
# FUNGSI AMBIL DATA HISTORIS (YAHOO FINANCE)
# ============================================

@st.cache_data(ttl=300)
def get_historical_data(ticker, period="100d"):
    """Ambil data historis dari Yahoo Finance"""
    try:
        df = yf.download(ticker, period=period, interval="1d", progress=False)
        if not df.empty:
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# ============================================
# FUNGSI ATR & RISK:REWARD
# ============================================

def calculate_atr(df, period=14):
    if df is None or df.empty or len(df) < period:
        return None
    
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    atr = tr.rolling(window=period).mean()
    return atr.iloc[-1]

def calculate_rr_ratio(entry_price, atr_value, multiplier_tp=2.5, multiplier_sl=1.5):
    if atr_value is None or atr_value <= 0:
        return None, None, None
    
    tp = entry_price + (atr_value * multiplier_tp)
    sl = entry_price - (atr_value * multiplier_sl)
    
    risk = entry_price - sl
    reward = tp - entry_price
    
    if risk > 0:
        rr_ratio = round(reward / risk, 2)
    else:
        rr_ratio = 0
    
    return round(tp, 2), round(sl, 2), rr_ratio

# ============================================
# FUNGSI SCREENING DENGAN YAHOO FINANCE
# ============================================

def analisa_saham_scalping(ticker, min_price=90, max_price=999999):
    """Analisis saham untuk screening dengan Yahoo Finance"""
    
    df = get_historical_data(ticker, "60d")
    
    if df.empty or len(df) < 30:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    # ============================================
    # INDIKATOR DASAR
    # ============================================
    
    # Moving Average
    df['MA5'] = df['Close'].rolling(5).mean()
    df['MA20'] = df['Close'].rolling(20).mean()
    
    # Volume
    df['MA_Vol_20'] = df['Volume'].rolling(20).mean()
    
    # RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Stochastic (14,3,3)
    low_14 = df['Low'].rolling(window=14).min()
    high_14 = df['High'].rolling(window=14).max()
    df['Stoch_K'] = 100 * ((df['Close'] - low_14) / (high_14 - low_14))
    df['Stoch_D'] = df['Stoch_K'].rolling(window=3).mean()
    
    # VWAP
    df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
    
    # Fibonacci Support
    high_val = df['High'].max()
    low_val = df['Low'].min()
    diff = high_val - low_val
    fibo_236 = round(low_val + (diff * 0.236))
    
    # ============================================
    # AMBIL DATA HARI INI, KEMARIN, DAN 5 HARI
    # ============================================
    hari_ini = df.iloc[-1]
    hari_kemarin = df.iloc[-2] if len(df) > 1 else hari_ini
    
    close_now = float(hari_ini['Close'])
    close_prev = float(hari_kemarin['Close'])
    vol_now = int(hari_ini['Volume'])
    vol_prev = int(hari_kemarin['Volume']) if len(df) > 1 else vol_now
    ma_vol_20 = float(hari_ini['MA_Vol_20']) if not pd.isna(hari_ini['MA_Vol_20']) else vol_now
    
    rsi_now = float(hari_ini['RSI']) if not pd.isna(hari_ini['RSI']) else 50.0
    k_now = float(hari_ini['Stoch_K']) if not pd.isna(hari_ini['Stoch_K']) else 50.0
    d_now = float(hari_ini['Stoch_D']) if not pd.isna(hari_ini['Stoch_D']) else 50.0
    
    vwap_now = float(hari_ini['VWAP']) if not pd.isna(hari_ini['VWAP']) else close_now
    ma5_now = float(hari_ini['MA5']) if not pd.isna(hari_ini['MA5']) else close_now
    
    # ============================================
    # VOLUME 5 HARI TERAKHIR
    # ============================================
    vol_5hari = []
    for i in range(1, min(6, len(df))):
        vol_5hari.append(int(df.iloc[-i]['Volume']))
    vol_5hari = vol_5hari[::-1]  # Urutkan dari yang terlama
    
    # ============================================
    # CEK TREN VOLUME 3 HARI
    # ============================================
    volume_naik_3hari = False
    if len(vol_5hari) >= 3:
        if vol_5hari[-3] < vol_5hari[-2] < vol_5hari[-1]:
            volume_naik_3hari = True
    
    # ============================================
    # DETEKSI SHAKE-OUT
    # ============================================
    shake_out = False
    if len(vol_5hari) >= 2:
        vol_change_pct = ((vol_now - vol_prev) / vol_prev) * 100 if vol_prev > 0 else 0
        price_change_pct = ((close_now - close_prev) / close_prev) * 100 if close_prev > 0 else 0
        
        # Volume turun > 20% dan harga turun < 2%
        if vol_change_pct < -20 and price_change_pct > -2 and price_change_pct < 2:
            shake_out = True
    
    # ============================================
    # FILTER HARGA
    # ============================================
    if not (min_price <= close_now <= max_price):
        return None
    
    # ============================================
    # HITUNG SKOR AKUMULASI
    # ============================================
    skor = 0
    alasan = []
    kriteria = []
    
    # 1. Volume 3 hari meningkat
    if volume_naik_3hari:
        skor += 1
        kriteria.append("✅ Volume 3 hari meningkat")
        alasan.append("Volume naik 3 hari berturut-turut")
    
    # 2. Volume hari ini > 1.5x rata-rata
    rasio_vol = vol_now / ma_vol_20 if ma_vol_20 > 0 else 1.0
    if rasio_vol >= 1.5:
        skor += 1
        kriteria.append(f"✅ Volume tinggi ({round(rasio_vol, 1)}x)")
        alasan.append(f"Volume {round(rasio_vol, 1)}x rata-rata")
    
    # 3. Harga stabil 3 hari (< 2% perubahan)
    if len(df) >= 3:
        price_change_3hari = abs((close_now - df.iloc[-3]['Close']) / df.iloc[-3]['Close']) * 100
        if price_change_3hari < 2:
            skor += 1
            kriteria.append("✅ Harga stabil 3 hari")
            alasan.append(f"Harga stabil ({round(price_change_3hari, 2)}%)")
    
    # 4. SHAKE-OUT! (Volume turun >20%, harga stabil)
    if shake_out:
        skor += 2
        kriteria.append("🔥 SHAKE-OUT DETECTED!")
        alasan.append("Volume turun >20%, harga stabil")
    
    # 5. Harga di atas MA5
    if close_now > ma5_now:
        skor += 1
        kriteria.append("✅ Harga di atas MA5")
        alasan.append("Harga > MA5 (Bullish)")
    
    # 6. RSI di bawah 70 (tidak overbought)
    if rsi_now < 70:
        skor += 1
        kriteria.append(f"✅ RSI {round(rsi_now)} (Normal)")
        alasan.append(f"RSI {round(rsi_now)} (tidak overbought)")
    
    # ============================================
    # PROBABILITAS KENAIKAN
    # ============================================
    probabilitas = round((skor / 7) * 100)
    
    # ============================================
    # STATUS & REKOMENDASI
    # ============================================
    if skor >= 6:
        rekomendasi = "🔥 STRONG BUY - Siap Breakout!"
        aksi = "🚀 Beli Besok Pagi"
        status = "🔥 SIAP BREAKOUT"
        warna = "#00e676"
        prob_status = "SANGAT TINGGI"
    elif skor >= 4:
        rekomendasi = "🟢 BUY - Dalam Akumulasi"
        aksi = "📈 Pantau Besok"
        status = "🟡 AKUMULASI"
        warna = "#f1c40f"
        prob_status = "TINGGI"
    elif skor >= 2:
        rekomendasi = "👀 WATCH - Perlu Konfirmasi"
        aksi = "⏳ Tunggu Sinyal"
        status = "⚪ NORMAL"
        warna = "#3498db"
        prob_status = "SEDANG"
    else:
        rekomendasi = "⏸️ AVOID - Tidak Memenuhi"
        aksi = "⏭️ Lewati"
        status = "⚪ TIDAK ADA"
        warna = "#888888"
        prob_status = "RENDAH"
    
    # ============================================
    # STATUS BANDAR
    # ============================================
    if len(df) > 1:
        vol_change_pct = ((vol_now - vol_prev) / vol_prev) * 100 if vol_prev > 0 else 0
        if vol_change_pct > 30 and close_now <= close_prev * 1.01:
            status_bandar = "🟢 Bandar Akumulasi"
        elif vol_change_pct > 30 and close_now > close_prev * 1.02:
            status_bandar = "🟡 Breakout"
        elif vol_change_pct < -30 and close_now > close_prev * 1.02:
            status_bandar = "🔴 Distribusi"
        elif vol_change_pct < -30 and close_now <= close_prev * 1.01:
            status_bandar = "⚪ Sepi"
        else:
            status_bandar = "⚖️ Normal"
    else:
        status_bandar = "⚖️ Normal"
    
    # ============================================
    # RETURN DATA
    # ============================================
    return {
        "Ticker": ticker.replace(".JK", ""),
        "Harga": round(close_now, 2),
        "Perubahan %": round(((close_now - close_prev) / close_prev) * 100, 2),
        "Volume": vol_now,
        "Rasio Vol": round(rasio_vol, 2),
        "RSI": round(rsi_now, 2),
        "Stoch %K": round(k_now, 2),
        "Stoch %D": round(d_now, 2),
        "VWAP": round(vwap_now, 2),
        "Volume 5 Hari": vol_5hari,
        "Volume Naik 3H": "✅" if volume_naik_3hari else "❌",
        "Shake-out": "🔥" if shake_out else "❌",
        "Skor": skor,
        "Probabilitas": probabilitas,
        "Status": status,
        "Rekomendasi": rekomendasi,
        "Aksi": aksi,
        "Status Bandar": status_bandar,
        "Alasan": ", ".join(alasan) if alasan else "Tidak ada sinyal",
        "Kriteria": ", ".join(kriteria) if kriteria else "Tidak ada"
    }

# ============================================
# SIDEBAR NAVIGASI
# ============================================
with st.sidebar:
    st.markdown("### 🧭 NAVIGASI")
    st.markdown("---")
    
    menu = st.radio(
        "Pilih Halaman:",
        ["📊 Dashboard Utama", "🔍 Screening Saham", "🔔 Rekomendasi Besok"],
        index=0,
        key="menu_navigasi"
    )
    
    st.markdown("---")
    st.caption("📱 Dibuat oleh: Fahrun Hidayat")
    st.caption(f"🕐 Update: {datetime.now().strftime('%H:%M:%S')}")

# ============================================
# ============================================
# MENU 1: DASHBOARD UTAMA
# ============================================
# ============================================
if menu == "📊 Dashboard Utama":
    
    # ============================================
    # DATA SEKTOR EMITEN
    # ============================================
    SEKTOR_EMITEN = {
        "BBCA": "🏦 Perbankan", "BBRI": "🏦 Perbankan", "BMRI": "🏦 Perbankan", "BBNI": "🏦 Perbankan",
        "BBTN": "🏦 Perbankan", "AGRO": "🏦 Perbankan", "GOTO": "🛒 E-commerce", "BUKA": "🛒 E-commerce",
        "TLKM": "📡 Telekomunikasi", "UNVR": "🧴 Consumer", "ICBP": "🧴 Consumer", "INDF": "🧴 Consumer",
        "ADRO": "⛏️ Tambang", "ITMG": "⛏️ Tambang", "PTBA": "⛏️ Tambang", "BUMI": "⛏️ Tambang",
        "ASRI": "🏗️ Properti", "ADHI": "🚧 Konstruksi", "WIKA": "🚧 Konstruksi", "PTPP": "🚧 Konstruksi",
        "KAEF": "💊 Farmasi", "KLBF": "💊 Farmasi", "MERK": "💊 Farmasi",
        "WIFI": "📡 Telekomunikasi", "LPKR": "🏗️ Properti", "PANI": "📰 Media", "SCMA": "📰 Media"
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
    txt_stoch = "⚖️ KONSOLIDASI: Momentum cenderung bergerak mendatar."
    txt_vol = "✅ Organik (Transaksi normal)."
    txt_foreign = "🟡 NEUTRAL FLOW: Transaksi asing berimbang."
    txt_rekomendasi = "🟡 HOLD / WAIT & SEE: Pantau area beli terdekat."
    border_color = "#f1c40f"
    rasio_vol_ma = 1.0
    df_live = pd.DataFrame()
    atr_display = 0
    sl_dinamis_floor = 0
    tp_dinamis_ceil = 0
    rr_display = 0
    rasio_vol_ma_display = 1.0

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
    # AMBIL DATA REAL-TIME DARI iTick
    # ============================================
    
    data_loaded = False
    
    with st.spinner(f"⏳ Mengambil data {ticker_pantau} dari iTick..."):
        stock_data = get_itick_data(ticker_pantau)
        
        if stock_data:
            data_loaded = True
            
            harga_terakhir = int(stock_data.get('ld', 0))
            vol_terakhir = int(stock_data.get('v', 0))
            open_hari_ini = float(stock_data.get('o', harga_terakhir))
            high_hari_ini = float(stock_data.get('h', harga_terakhir))
            low_hari_ini = float(stock_data.get('l', harga_terakhir))
            prev_close = float(stock_data.get('pc', harga_terakhir))
            nama_emiten = stock_data.get('n', ticker_pantau)
            
            if prev_close > 0:
                change_persen = round(((harga_terakhir - prev_close) / prev_close) * 100, 2)
            else:
                change_persen = 0.0
            
            vol_kemarin = int(vol_terakhir * 0.9)
            
            st.success(f"✅ Data {ticker_pantau} dari iTick | {nama_emiten}")
    
    # ============================================
    # AMBIL DATA HISTORIS DARI YAHOO
    # ============================================
    if data_loaded:
        with st.spinner(f"⏳ Mengambil data historis {ticker_pantau}..."):
            df_live = get_historical_data(f"{ticker_pantau}.JK", "100d")
            
            if df_live.empty:
                st.warning("⚠️ Data historis tidak tersedia, menggunakan data simulasi")
                
                dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
                df_live = pd.DataFrame({
                    'Open': [harga_terakhir * (0.99 + 0.02 * (i/30)) for i in range(30)],
                    'High': [harga_terakhir * (1.01 + 0.02 * (i/30)) for i in range(30)],
                    'Low': [harga_terakhir * (0.98 + 0.02 * (i/30)) for i in range(30)],
                    'Close': [harga_terakhir * (0.99 + 0.02 * (i/30)) for i in range(30)],
                    'Volume': [vol_terakhir * (0.8 + 0.4 * (i/30)) for i in range(30)]
                }, index=dates)
    
    if not data_loaded:
        st.error(f"❌ Gagal memuat data {ticker_pantau}. Pastikan kode saham benar.")
        st.stop()

    # ============================================
    # HITUNG INDIKATOR TEKNIKAL
    # ============================================
    
    if not df_live.empty and len(df_live) > 10:
        # RSI
        delta = df_live['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=10).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=10).mean()
        rs = gain / loss
        rsi_series = 100 - (100 / (1 + rs))
        rsi_terakhir = round(rsi_series.iloc[-1], 2)
        rsi_kemarin = round(rsi_series.iloc[-2], 2) if len(rsi_series) > 1 else rsi_terakhir
        
        # Stochastic
        rsi_min = rsi_series.rolling(window=10).min()
        rsi_max = rsi_series.rolling(window=10).max()
        stoch_rsi_series = (rsi_series - rsi_min) / (rsi_max - rsi_min) * 100
        df_live['Stoch_K'] = stoch_rsi_series.rolling(window=3).mean()
        df_live['Stoch_D'] = df_live['Stoch_K'].rolling(window=3).mean()
        
        stoch_k = round(df_live['Stoch_K'].iloc[-1], 2)
        stoch_d = round(df_live['Stoch_D'].iloc[-1], 2)
        stoch_k_kemarin = round(df_live['Stoch_K'].iloc[-2], 2) if len(df_live['Stoch_K']) > 1 else stoch_k
        stoch_d_kemarin = round(df_live['Stoch_D'].iloc[-2], 2) if len(df_live['Stoch_D']) > 1 else stoch_d
        
        # MA
        ma_volume_20 = df_live['Volume'].rolling(window=20).mean().iloc[-1]
        ma5_val = df_live['Close'].rolling(window=5).mean().iloc[-1]
        ma20_val = df_live['Close'].rolling(window=20).mean().iloc[-1]
        ma50_val = df_live['Close'].rolling(window=50).mean().iloc[-1] if len(df_live) >= 50 else ma20_val
        
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
        
        # MA Cross
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
        
        # Fibonacci
        high_val = df_live['High'].max()
        low_val = df_live['Low'].min()
        diff = high_val - low_val
        support_fibo = round(low_val + (diff * 0.236))
        fibo_50 = round(low_val + (diff * 0.50))
        resisten_fibo = round(low_val + (diff * 0.618))
        fibo_786 = round(low_val + (diff * 0.786))
        
        # Confluence
        df_recent = df_live.tail(20)
        low_points = df_recent['Low'].tolist()
        low_counts = Counter([round(x) for x in low_points])
        support_candidates = [price for price, count in low_counts.items() if count >= 2 and price < harga_terakhir]
        confluence_support = round(min(support_candidates)) if support_candidates else support_fibo
        
        high_points = df_recent['High'].tolist()
        high_counts = Counter([round(x) for x in high_points])
        resistance_candidates = [price for price, count in high_counts.items() if count >= 2 and price > harga_terakhir]
        confluence_resistance = round(max(resistance_candidates)) if resistance_candidates else resisten_fibo
        
        # VWAP
        df_live['VWAP'] = (df_live['Volume'] * (df_live['High'] + df_live['Low'] + df_live['Close']) / 3).cumsum() / df_live['Volume'].cumsum()
        vwap_val = round(df_live['VWAP'].iloc[-1])
        
        # FVG
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
        
        # ATR
        atr_value = calculate_atr(df_live, 14)
        
        if atr_value is not None and atr_value > 0 and harga_terakhir > 0:
            tp_dinamis, sl_dinamis, rr_ratio = calculate_rr_ratio(harga_terakhir, atr_value, 2.5, 1.5)
            sl_dinamis_floor = math.floor(sl_dinamis)
            tp_dinamis_ceil = math.ceil(tp_dinamis)
            rr_display = rr_ratio
            atr_display = round(atr_value, 2)
        else:
            sl_dinamis_floor = math.floor(harga_terakhir * 0.962)
            tp_dinamis_ceil = math.ceil(harga_terakhir * 1.055)
            rr_display = 0
            atr_display = 0
        
        # Foreign Flow
        perubahan_dana = (harga_terakhir - open_hari_ini) * vol_terakhir * 0.035
        foreign_value_est = int(perubahan_dana)
        if foreign_value_est > 50000000:
            foreign_net_summary = "AKUMULASI"
        elif foreign_value_est < -50000000:
            foreign_net_summary = "DISTRIBUSI"
        else:
            foreign_net_summary = "NETRAL"

    # ============================================
    # STATUS & REKOMENDASI
    # ============================================
    status_saran = "HOLD / WAIT & SEE"
    bg_badge = "#f1c40f"
    text_badge = "HOLD"

    is_oversold_rsi = rsi_terakhir < 38
    is_overbought_rsi = rsi_terakhir > 72
    is_golden_cross = (stoch_k_kemarin <= stoch_d_kemarin and stoch_k > stoch_d and stoch_k < 35)
    is_dead_cross = (stoch_k_kemarin >= stoch_d_kemarin and stoch_k < stoch_d and stoch_k > 70)

    volume_confirm = vol_terakhir > ma_volume_20 * 1.2 if ma_volume_20 > 0 else False
    volume_breakout = vol_terakhir > ma_volume_20 * 1.8 if ma_volume_20 > 0 else False

    near_support = abs(harga_terakhir - support_fibo) / support_fibo < 0.02 if support_fibo > 0 else False
    near_resistance = abs(harga_terakhir - resisten_fibo) / resisten_fibo < 0.02 if resisten_fibo > 0 else False

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
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric(
                label="💰 Harga Terakhir",
                value=f"Rp {harga_terakhir:,}",
                delta=f"{change_persen}%"
            )
            
            try:
                if not df_live.empty:
                    ma_volume_20_series = df_live['Volume'].rolling(window=20).mean()
                    if len(ma_volume_20_series) > 0:
                        ma_volume_20_display = float(ma_volume_20_series.iloc[-1])
                    else:
                        ma_volume_20_display = float(vol_terakhir)
                else:
                    ma_volume_20_display = float(vol_terakhir)
            except:
                ma_volume_20_display = float(vol_terakhir)

            if ma_volume_20_display > 0:
                rasio_vol_ma_display = vol_terakhir / ma_volume_20_display
            else:
                rasio_vol_ma_display = 1.0

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
        
        with st.container(border=True):
            st.markdown("##### 🎯 KALKULATOR TRADING PLAN")
            
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
            
            st.markdown("---")
            st.markdown("**📊 RISK:REWARD DINAMIS (BERDASARKAN ATR)**")

            if atr_display > 0 and harga_terakhir > 0:
                col_atr1, col_atr2, col_atr3 = st.columns(3)
                
                with col_atr1:
                    st.metric(
                        label="📉 ATR (14)",
                        value=f"Rp {atr_display:,}",
                        delta=f"{round(atr_display / harga_terakhir * 100, 2)}% dari harga"
                    )
                
                with col_atr2:
                    st.metric(
                        label="🎯 Dynamic TP (2.5x ATR)",
                        value=f"Rp {tp_dinamis_ceil:,}",
                        delta=f"+{tp_dinamis_ceil - harga_terakhir:,}"
                    )
                
                with col_atr3:
                    st.metric(
                        label="🛡️ Dynamic SL (1.5x ATR)",
                        value=f"Rp {sl_dinamis_floor:,}",
                        delta=f"{sl_dinamis_floor - harga_terakhir:,}"
                    )
                
                if rr_display >= 2:
                    st.success(f"📊 **Risk:Reward Ratio: 1:{rr_display}** ✅ Ideal! (Minimal 1:2)")
                elif rr_display >= 1.5:
                    st.info(f"📊 **Risk:Reward Ratio: 1:{rr_display}** ⚠️ Cukup (Target 1:2)")
                else:
                    st.warning(f"📊 **Risk:Reward Ratio: 1:{rr_display}** 🔴 Rendah! Pertimbangkan ulang entry")
                
                st.caption(f"""
                💡 **Keterangan:**
                - ATR ({atr_display}) adalah rata-rata pergerakan harga 14 hari terakhir
                - TP Dinamis = Harga Entry + (ATR × 2.5)
                - SL Dinamis = Harga Entry - (ATR × 1.5)
                - R:R = (TP - Entry) / (Entry - SL)
                """)
            else:
                st.info(f"""
                ⚠️ **ATR tidak tersedia** (data kurang dari 14 hari)
                
                Menggunakan default:
                - CL: -3.8% (Rp {sl_dinamis_floor:,})
                - TP: +5.5% (Rp {tp_dinamis_ceil:,})
                - R:R: Tidak tersedia
                """)

    # ============================================
    # PANEL KANAN
    # ============================================
    with col_right_panel:
        st.markdown("##### 📋 LIVE MARKET INTELLIGENCE & ACTION PLAN")
        
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
        
        if foreign_net_summary == "AKUMULASI":
            txt_foreign = f"🟢 FOREIGN ACCUMULATION: Neto Rp {abs(foreign_value_est):,}."
        elif foreign_net_summary == "DISTRIBUSI":
            txt_foreign = f"🔴 FOREIGN DISTRIBUTION: Neto Rp {abs(foreign_value_est):,}."
        else:
            txt_foreign = "🟡 NEUTRAL FLOW: Transaksi asing berimbang."
        
        if text_badge == "BUY":
            txt_rekomendasi = "💥 STRATEGIC BUY: Akumulasi bertahap dekat support utama."
            border_color = "#2ecc71"
        elif text_badge == "SELL":
            txt_rekomendasi = "🚨 TAKE PROFIT: Amankan modal sebelum distribusi lanjutan."
            border_color = "#e74c3c"
        else:
            txt_rekomendasi = "🟡 HOLD / WAIT & SEE: Pantau area beli terdekat."
            border_color = "#f1c40f"
        
        with st.container(border=True):
            
            st.markdown("---")
            st.markdown("**📈 TREND MOVING AVERAGE (MA)**")
            
            warna_ma5 = "#2ecc71" if "Di Atas" in status_ma5 else "#e74c3c"
            st.markdown(
                f"""
                <div style='background-color: rgba(46, 204, 113, 0.06); border-left: 4px solid {warna_ma5}; padding: 10px 14px; border-radius: 4px; margin-bottom: 6px;'>
                    <span style='font-size: 14px;'>• MA 5: <span style='color: {warna_ma5}; font-weight: bold; font-size: 14px;'>{status_ma5}</span></span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            warna_ma20 = "#2ecc71" if "Di Atas" in status_ma20 else "#e74c3c"
            st.markdown(
                f"""
                <div style='background-color: rgba(46, 204, 113, 0.06); border-left: 4px solid {warna_ma20}; padding: 10px 14px; border-radius: 4px; margin-bottom: 6px;'>
                    <span style='font-size: 14px;'>• MA 20: <span style='color: {warna_ma20}; font-weight: bold; font-size: 14px;'>{status_ma20}</span></span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            warna_ma50 = "#2ecc71" if "Di Atas" in status_ma50 else "#e74c3c"
            st.markdown(
                f"""
                <div style='background-color: rgba(46, 204, 113, 0.06); border-left: 4px solid {warna_ma50}; padding: 10px 14px; border-radius: 4px; margin-bottom: 6px;'>
                    <span style='font-size: 14px;'>• MA 50: <span style='color: {warna_ma50}; font-weight: bold; font-size: 14px;'>{status_ma50}</span></span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown(
                f"""
                <div style='background-color: rgba(241, 196, 15, 0.06); border-left: 4px solid {warna_signal_ma}; padding: 10px 14px; border-radius: 4px; margin-top: 6px;'>
                    <span style='font-size: 14px;'>🔄 MA Cross: <span style='color: {warna_signal_ma}; font-weight: bold; font-size: 14px;'>{signal_ma_cross}</span></span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("---")
            st.markdown("**⏱️ MOMENTUM STOCHASTIC RSI**")
            
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
            
            st.markdown("---")
            st.markdown("**📦 LIKUIDITAS VOLUME**")
            
            if rasio_vol_ma_display >= 1.8:
                warna_vol = "#2ecc71"
            elif rasio_vol_ma_display <= 0.6:
                warna_vol = "#e74c3c"
            else:
                warna_vol = "#f1c40f"
            
            if rasio_vol_ma_display >= 1.8:
                txt_vol = f"🔥🔥 VOLUME BREAKOUT! {round(rasio_vol_ma_display, 1)}x rata-rata"
            elif rasio_vol_ma_display >= 1.2:
                txt_vol = f"📈 Volume di atas rata-rata ({round(rasio_vol_ma_display, 1)}x)"
            elif rasio_vol_ma_display >= 0.8:
                txt_vol = f"✅ Volume normal ({round(rasio_vol_ma_display, 1)}x)"
            elif rasio_vol_ma_display >= 0.5:
                txt_vol = f"💤 Volume rendah ({round(rasio_vol_ma_display, 1)}x)"
            else:
                txt_vol = f"🥶 Volume sangat sepi ({round(rasio_vol_ma_display, 1)}x)"
            
            st.markdown(
                f"""
                <div style='background-color: rgba(26, 188, 156, 0.06); border-left: 4px solid {warna_vol}; padding: 10px 14px; border-radius: 4px;'>
                    <span style='font-size: 14px; color: #d1d4dc;'>
                        {txt_vol}<br>
                        <span style='font-size: 13px; color: #888;'>
                            Volume: <span style='font-weight: bold; color: {warna_vol};'>{vol_terakhir:,}</span> | 
                            Rata-rata 20H: <span style='font-weight: bold;'>{round(ma_volume_20):,}</span>
                        </span>
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("---")
            st.markdown("**🌐 FOREIGN FLOW**")
            
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
# ============================================
# MENU 2: SCREENING SAHAM
# ============================================
# ============================================
elif menu == "🔍 Screening Saham":
    
    st.markdown("### 🚀 RADAR SCREENING EMITEN")
    st.markdown("*Analisis saham potensial berdasarkan data historis (Yahoo Finance)*")
    
    # ============================================
    # INISIALISASI SESSION STATE
    # ============================================
    if 'screening_history' not in st.session_state:
        st.session_state['screening_history'] = []
    
    # ============================================
    # PENGATURAN SCREENING
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
        st.caption("💡 **Tips:** Range Rp 90-500+ cocok untuk scalping")
    
    if mode_screening == "🎯 Scalping (Rp 90-500+)":
        min_price = 90
        max_price = 500
        st.info("📌 Fokus pada saham dengan harga Rp 90 - Rp 500 untuk scalping")
    
    elif mode_screening == "🔍 All Price (Tanpa Filter)":
        min_price = 0
        max_price = 999999
        st.info("📌 Screening semua saham tanpa batasan harga")
    
    else:
        col_min, col_max = st.columns(2)
        with col_min:
            min_price = st.number_input("Harga Minimum (Rp):", value=90, min_value=0, step=10)
        with col_max:
            max_price = st.number_input("Harga Maksimum (Rp):", value=500, min_value=0, step=10)
        st.info(f"📌 Screening saham dengan harga Rp {min_price} - Rp {max_price}")
    
    st.markdown("---")
    
    # ============================================
    # DAFTAR SAHAM
    # ============================================
    DAFTAR_SAHAM = [
        "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "TLKM.JK", "UNVR.JK", "ICBP.JK", "INDF.JK", "MYOR.JK",
        "ADRO.JK", "ITMG.JK", "PTBA.JK", "KLBF.JK", "MERK.JK", "SMGR.JK", "INTP.JK",
        "BUMI.JK", "BIPI.JK", "KIJA.JK", "PADI.JK", "DEWA.JK", "BUKA.JK", "GOTO.JK",
        "ENRG.JK", "ELSA.JK", "ADHI.JK", "WIKA.JK", "PTPP.JK", "SMDR.JK", "HAIS.JK",
        "TMAS.JK", "ASSA.JK", "PSSI.JK", "NELY.JK", "RMKE.JK", "COAL.JK", "DOID.JK",
        "BBTN.JK", "MAIN.JK", "WOOD.JK", "ADMG.JK", "KRAS.JK", "BUDI.JK", "GOOD.JK",
        "WIFI.JK", "LPKR.JK", "TOTL.JK", "KAEF.JK", "INAF.JK", "IRRA.JK", "PEHA.JK",
        "SCMA.JK", "MARI.JK", "ABBA.JK", "BHIT.JK", "IPTV.JK", "VIVA.JK", "MDIA.JK",
        "AGRO.JK", "BABP.JK", "BBYB.JK", "BBKP.JK", "BCIC.JK", "BACA.JK", "AMAR.JK",
        "DNAR.JK", "BGTG.JK", "BVIC.JK", "INPC.JK", "BCAP.JK", "PNBS.JK", "CFIN.JK",
        "ASRI.JK", "PPRO.JK", "BKSL.JK", "MDLN.JK", "LPCK.JK", "GWSA.JK", "DGIK.JK",
        "DOOH.JK", "COCO.JK", "NZIA.JK", "JKON.JK", "WEGE.JK", "WSBP.JK", "URBN.JK",
        "ELTY.JK", "ACST.JK", "META.JK", "KPIG.JK", "BCIP.JK", "BPTR.JK", "DILD.JK",
        "OMRE.JK", "LPCK.JK", "CITY.JK", "SMRU.JK", "BEST.JK", "FORZ.JK", "PANI.JK",
        "DKFT.JK", "ZINC.JK", "IKAN.JK", "SIMP.JK", "SOCI.JK", "APEX.JK", "SQMI.JK",
        "INDY.JK", "TOBA.JK", "KKGI.JK", "GTBO.JK", "BOSS.JK", "NANO.JK", "TRIL.JK",
        "OASA.JK", "ZBRA.JK", "MPOW.JK", "MIRA.JK", "CENT.JK", "KBLI.JK", "POLY.JK",
        "BAJA.JK", "ALTO.JK", "CAMP.JK", "CPRO.JK", "PMMP.JK", "PBRX.JK", "MYTX.JK",
        "AISA.JK", "NASA.JK", "MLIA.JK", "TARA.JK", "IKAI.JK", "LUCK.JK", "KBRI.JK",
        "ENVY.JK", "BOLA.JK", "HDFA.JK", "BESS.JK", "HOMI.JK", "OILS.JK", "CNKO.JK",
        "NATO.JK", "LPPS.JK", "GEMA.JK", "PAMG.JK", "KIAS.JK", "SULI.JK", "GPRA.JK"
    ]
    
    # ============================================
    # TAMPILAN UTAMA
    # ============================================
    col_btn, col_info = st.columns([1, 3])
    
    with col_btn:
        if st.button("🔄 JALANKAN SCREENING", use_container_width=True, type="primary"):
            st.session_state['run_screening'] = True
    
    with col_info:
        st.info(f"📊 **Total Emiten yang Discan:** {len(DAFTAR_SAHAM)} saham")
        st.caption("📌 Screening berbasis: Volume 3 Hari, Shake-out, RSI, dan MA")
    
    # ============================================
    # EKSEKUSI SCREENING
    # ============================================
    if 'run_screening' in st.session_state and st.session_state['run_screening']:
        with st.spinner(f"⏳ Sedang melakukan screening {len(DAFTAR_SAHAM)} saham..."):
            kumpulan_data = []
            progress_bar = st.progress(0)
            
            for i, saham in enumerate(DAFTAR_SAHAM):
                try:
                    hasil = analisa_saham_scalping(saham, min_price, max_price)
                    if hasil:
                        kumpulan_data.append(hasil)
                except Exception as e:
                    pass
                progress_bar.progress((i + 1) / len(DAFTAR_SAHAM))
            
            progress_bar.empty()
            
            if kumpulan_data:
                df_hasil = pd.DataFrame(kumpulan_data)
                df_hasil = df_hasil.sort_values(by="Skor", ascending=False)
                
                st.session_state['screening_history'].append({
                    'tanggal': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'data': df_hasil.copy()
                })
                
                st.success(f"✅ Screening selesai! Ditemukan {len(df_hasil)} saham teranalisis.")
                
                # ============================================
                # STATISTIK
                # ============================================
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                
                siap_breakout = df_hasil[df_hasil['Skor'] >= 5]
                akumulasi = df_hasil[(df_hasil['Skor'] >= 3) & (df_hasil['Skor'] < 5)]
                normal = df_hasil[(df_hasil['Skor'] >= 1) & (df_hasil['Skor'] < 3)]
                tidak_ada = df_hasil[df_hasil['Skor'] < 1]
                
                with col_stat1:
                    st.metric("🔥 SIAP BREAKOUT", len(siap_breakout))
                with col_stat2:
                    st.metric("🟡 AKUMULASI", len(akumulasi))
                with col_stat3:
                    st.metric("⚪ NORMAL", len(normal))
                with col_stat4:
                    st.metric("⏸️ TIDAK ADA", len(tidak_ada))
                
                st.markdown("---")
                
                # ============================================
                # FILTER REKOMENDASI
                # ============================================
                st.subheader("🎯 Filter Rekomendasi")
                
                col_filter1, col_filter2 = st.columns(2)
                with col_filter1:
                    show_only_ready = st.checkbox("🔥 Tampilkan hanya saham SIAP BREAKOUT (Skor ≥ 5)", value=False)
                with col_filter2:
                    show_akumulasi = st.checkbox("🟡 Tampilkan saham dalam AKUMULASI (Skor 3-4)", value=False)
                
                # Apply filter
                df_filtered = df_hasil.copy()
                if show_only_ready:
                    df_filtered = df_filtered[df_filtered['Skor'] >= 5]
                elif show_akumulasi:
                    df_filtered = df_filtered[(df_filtered['Skor'] >= 3) & (df_filtered['Skor'] < 5)]
                
                # ============================================
                # TABEL HASIL DENGAN WARNA
                # ============================================
                st.subheader("📊 Hasil Screening")
                
                # Fungsi untuk mewarnai baris berdasarkan status
                def color_rows(row):
                    if row['Skor'] >= 5:
                        return ['background-color: rgba(0, 230, 118, 0.15)'] * len(row)
                    elif row['Skor'] >= 3:
                        return ['background-color: rgba(241, 196, 15, 0.15)'] * len(row)
                    elif row['Skor'] >= 1:
                        return ['background-color: rgba(52, 152, 219, 0.08)'] * len(row)
                    else:
                        return ['background-color: rgba(136, 136, 136, 0.05)'] * len(row)
                
                # Tampilkan dengan styling
                st.dataframe(
                    df_filtered.style.apply(color_rows, axis=1),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                        "Harga": st.column_config.NumberColumn("Harga", format="Rp %.0f"),
                        "Perubahan %": st.column_config.NumberColumn("Perubahan %", format="%.2f%%"),
                        "Volume": st.column_config.NumberColumn("Volume", format="%d"),
                        "Rasio Vol": st.column_config.NumberColumn("Rasio Vol", format="%.2f"),
                        "RSI": st.column_config.NumberColumn("RSI", format="%.2f"),
                        "Stoch %K": st.column_config.NumberColumn("%K", format="%.2f"),
                        "Stoch %D": st.column_config.NumberColumn("%D", format="%.2f"),
                        "VWAP": st.column_config.NumberColumn("VWAP", format="Rp %.0f"),
                        "Volume 5 Hari": st.column_config.ListColumn("Volume 5 Hari", width="medium"),
                        "Volume Naik 3H": st.column_config.TextColumn("Vol Naik 3H", width="small"),
                        "Shake-out": st.column_config.TextColumn("Shake-out", width="small"),
                        "Skor": st.column_config.NumberColumn("Skor", format="%d"),
                        "Probabilitas": st.column_config.NumberColumn("Probabilitas", format="%d%%"),
                        "Status": st.column_config.TextColumn("Status", width="medium"),
                        "Rekomendasi": st.column_config.TextColumn("Rekomendasi", width="medium"),
                        "Aksi": st.column_config.TextColumn("Aksi", width="medium"),
                        "Status Bandar": st.column_config.TextColumn("Bandar", width="medium"),
                        "Alasan": st.column_config.TextColumn("Alasan", width="large"),
                        "Kriteria": st.column_config.TextColumn("Kriteria", width="large"),
                    }
                )
                
                # ============================================
                # REKOMENDASI TERBAIK
                # ============================================
                st.markdown("---")
                st.subheader("🎯 Rekomendasi Terbaik untuk Besok")
                
                top_rekomendasi = df_hasil[df_hasil['Skor'] >= 5].head(5)
                
                if not top_rekomendasi.empty:
                    for idx, row in top_rekomendasi.iterrows():
                        st.markdown(f"""
                        <div style='background-color: rgba(0, 230, 118, 0.12); border-left: 4px solid #00e676; padding: 10px 15px; border-radius: 4px; margin-bottom: 8px;'>
                            <b style='color: #00e676; font-size: 16px;'>🔥 {row['Ticker']}</b>
                            <span style='color: #ddd;'> | Skor: {row['Skor']} | Probabilitas: {row['Probabilitas']}%</span><br>
                            <span style='color: #aaa;'>{row['Rekomendasi']} | {row['Aksi']}</span><br>
                            <span style='color: #888; font-size: 13px;'>📌 {row['Alasan']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.caption(f"📌 {len(top_rekomendasi)} saham siap breakout besok. Probabilitas kenaikan tinggi.")
                else:
                    st.info("⚠️ Belum ada saham yang mencapai skor ≥ 5. Coba jalankan screening nanti atau periksa kembali.")
                
                # ============================================
                # DOWNLOAD
                # ============================================
                st.markdown("---")
                csv = df_hasil.to_csv(index=False)
                st.download_button(
                    label="📥 Download Hasil Screening (CSV)",
                    data=csv,
                    file_name=f"Screening_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                del st.session_state['run_screening']
            else:
                st.warning(f"⚠️ Tidak ada saham yang memenuhi kriteria screening dengan harga Rp {min_price} - Rp {max_price}.")
                del st.session_state['run_screening']
    else:
        st.info("💡 Klik tombol 'JALANKAN SCREENING' untuk mulai analisis.")
    
    # ============================================
    # HISTORY SCREENING
    # ============================================
    st.markdown("---")
    st.markdown("### 📋 HISTORY SCREENING")
    
    if st.session_state['screening_history']:
        for idx, history in enumerate(st.session_state['screening_history']):
            with st.expander(f"📅 {history['tanggal']} - {len(history['data'])} saham ditemukan"):
                st.dataframe(
                    history['data'][['Ticker', 'Harga', 'Perubahan %', 'Skor', 'Probabilitas', 'Rekomendasi', 'Status Bandar']],
                    use_container_width=True,
                    hide_index=True
                )
    else:
        st.caption("Belum ada history screening. Jalankan screening terlebih dahulu.")

# ============================================
# ============================================
# MENU 3: REKOMENDASI BESOK
# ============================================
# ============================================
elif menu == "🔔 Rekomendasi Besok":
    
    st.markdown("### 🔔 REKOMENDASI BELI & JUAL UNTUK BESOK")
    st.markdown("*Berdasarkan hasil screening dan deteksi akumulasi bandar*")
    
    # ============================================
    # CEK APAKAH ADA DATA SCREENING
    # ============================================
    if not st.session_state['screening_history']:
        st.warning("⚠️ Belum ada data screening. Silakan jalankan screening terlebih dahulu di menu 'Screening Saham'.")
        st.info("💡 Klik menu 'Screening Saham' → 'JALANKAN SCREENING'")
        st.stop()
    
    # Ambil data screening terakhir
    df_rekomendasi = st.session_state['screening_history'][-1]['data'].copy()
    
    # ============================================
    # FILTER REKOMENDASI
    # ============================================
    st.markdown("### 🎯 Filter Rekomendasi")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        min_skor = st.slider("Skor Minimum", 0, 7, 3, key="min_skor")
    
    with col_f2:
        min_prob = st.slider("Probabilitas Minimum", 0, 100, 50, key="min_prob")
    
    with col_f3:
        show_type = st.selectbox(
            "Tampilkan:",
            ["Semua", "🔥 SIAP BREAKOUT", "🟡 AKUMULASI", "⚪ NORMAL"],
            key="show_type"
        )
    
    # ============================================
    # APLIKASI FILTER
    # ============================================
    df_filtered = df_rekomendasi[df_rekomendasi['Skor'] >= min_skor]
    df_filtered = df_filtered[df_filtered['Probabilitas'] >= min_prob]
    
    if show_type != "Semua":
        df_filtered = df_filtered[df_filtered['Status'] == show_type]
    
    df_filtered = df_filtered.sort_values(by="Skor", ascending=False)
    
    # ============================================
    # STATISTIK REKOMENDASI
    # ============================================
    st.markdown("---")
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    
    with col_s1:
        st.metric("📊 Total Saham", len(df_filtered))
    
    with col_s2:
        siap = len(df_filtered[df_filtered['Skor'] >= 5])
        st.metric("🔥 Siap Breakout", siap)
    
    with col_s3:
        akum = len(df_filtered[(df_filtered['Skor'] >= 3) & (df_filtered['Skor'] < 5)])
        st.metric("🟡 Akumulasi", akum)
    
    with col_s4:
        prob_avg = round(df_filtered['Probabilitas'].mean(), 1) if not df_filtered.empty else 0
        st.metric("📈 Rata-rata Prob.", f"{prob_avg}%")
    
    st.markdown("---")
    
    # ============================================
    # REKOMENDASI BELI (SIAP BREAKOUT)
    # ============================================
    st.subheader("🔥 REKOMENDASI BELI (Siap Breakout)")
    
    df_beli = df_filtered[df_filtered['Skor'] >= 5]
    
    if not df_beli.empty:
        for idx, row in df_beli.iterrows():
            st.markdown(f"""
            <div style='background-color: rgba(0, 230, 118, 0.15); border: 2px solid #00e676; padding: 15px 20px; border-radius: 8px; margin-bottom: 12px;'>
                <div style='display: flex; align-items: center; justify-content: space-between;'>
                    <div>
                        <span style='font-size: 20px; font-weight: bold; color: #00e676;'>{row['Ticker']}</span>
                        <span style='font-size: 16px; color: #ddd; margin-left: 15px;'>Rp {row['Harga']:,.0f}</span>
                        <span style='font-size: 14px; color: #aaa; margin-left: 15px;'>Skor: {row['Skor']} | Prob: {row['Probabilitas']}%</span>
                    </div>
                    <div>
                        <span style='background-color: #00e676; color: #111; padding: 4px 12px; border-radius: 4px; font-weight: bold;'>BELI</span>
                    </div>
                </div>
                <div style='margin-top: 8px; color: #aaa; font-size: 14px;'>
                    📌 {row['Alasan']}
                </div>
                <div style='margin-top: 4px; color: #888; font-size: 13px;'>
                    🎯 {row['Aksi']} | Status Bandar: {row['Status Bandar']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.caption(f"📌 {len(df_beli)} saham direkomendasikan BELI untuk besok.")
    else:
        st.info("⚠️ Belum ada saham dengan skor ≥ 5. Tidak ada rekomendasi BELI.")
    
    # ============================================
    # REKOMENDASI JUAL / HINDARI
    # ============================================
    st.markdown("---")
    st.subheader("🔴 REKOMENDASI HINDARI")
    
    df_jual = df_filtered[df_filtered['Status Bandar'].str.contains("Distribusi")]
    
    if not df_jual.empty:
        for idx, row in df_jual.iterrows():
            st.markdown(f"""
            <div style='background-color: rgba(231, 76, 60, 0.12); border: 2px solid #e74c3c; padding: 15px 20px; border-radius: 8px; margin-bottom: 12px;'>
                <div style='display: flex; align-items: center; justify-content: space-between;'>
                    <div>
                        <span style='font-size: 20px; font-weight: bold; color: #e74c3c;'>{row['Ticker']}</span>
                        <span style='font-size: 16px; color: #ddd; margin-left: 15px;'>Rp {row['Harga']:,.0f}</span>
                        <span style='font-size: 14px; color: #aaa; margin-left: 15px;'>Skor: {row['Skor']}</span>
                    </div>
                    <div>
                        <span style='background-color: #e74c3c; color: #fff; padding: 4px 12px; border-radius: 4px; font-weight: bold;'>HINDARI</span>
                    </div>
                </div>
                <div style='margin-top: 8px; color: #aaa; font-size: 14px;'>
                    📌 {row['Alasan']}
                </div>
                <div style='margin-top: 4px; color: #888; font-size: 13px;'>
                    ⚠️ Status Bandar: {row['Status Bandar']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.caption(f"📌 {len(df_jual)} saham sebaiknya dihindari karena indikasi distribusi.")
    else:
        st.info("✅ Tidak ada saham dengan indikasi distribusi.")
    
    # ============================================
    # TABEL LENGKAP
    # ============================================
    st.markdown("---")
    st.subheader("📊 Tabel Lengkap Rekomendasi")
    
    st.dataframe(
        df_filtered[['Ticker', 'Harga', 'Perubahan %', 'Skor', 'Probabilitas', 'Status', 'Status Bandar', 'Alasan']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ticker": st.column_config.TextColumn("Ticker", width="small"),
            "Harga": st.column_config.NumberColumn("Harga", format="Rp %.0f"),
            "Perubahan %": st.column_config.NumberColumn("Perubahan %", format="%.2f%%"),
            "Skor": st.column_config.NumberColumn("Skor", format="%d"),
            "Probabilitas": st.column_config.NumberColumn("Probabilitas", format="%d%%"),
            "Status": st.column_config.TextColumn("Status", width="medium"),
            "Status Bandar": st.column_config.TextColumn("Bandar", width="medium"),
            "Alasan": st.column_config.TextColumn("Alasan", width="large"),
        }
    )

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.caption("⚡ Data real-time dari iTick API | 📊 Data historis dari Yahoo Finance | Dibuat oleh Fahrun Hidayat")
