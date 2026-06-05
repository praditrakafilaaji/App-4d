# rekap_4d_pro.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import random

# ==================== KONFIGURASI HALAMAN ====================
st.set_page_config(
    page_title="Rekap 4D Pro - AI Prediksi Angka Main",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== SHIO DATABASE ====================
DATA_SHIO = {
    "Tikus": [1, 13, 25, 37, 49, 61, 73, 85, 97],
    "Kerbau": [2, 14, 26, 38, 50, 62, 74, 86, 98],
    "Macan": [3, 15, 27, 39, 51, 63, 75, 87, 99],
    "Kelinci": [4, 16, 28, 40, 52, 64, 76, 88, 0],
    "Naga": [5, 17, 29, 41, 53, 65, 77, 89],
    "Ular": [6, 18, 30, 42, 54, 66, 78, 90],
    "Kuda": [7, 19, 31, 43, 55, 67, 79, 91],
    "Kambing": [8, 20, 32, 44, 56, 68, 80, 92],
    "Monyet": [9, 21, 33, 45, 57, 69, 81, 93],
    "Ayam": [10, 22, 34, 46, 58, 70, 82, 94],
    "Anjing": [11, 23, 35, 47, 59, 71, 83, 95],
    "Babi": [12, 24, 36, 48, 60, 72, 84, 96]
}

# ==================== FUNGSI BANTU ====================
def format_4d(val):
    """Format angka menjadi 4 digit"""
    str_val = str(val).strip()
    if len(str_val) == 1:
        return f"000{str_val}"
    elif len(str_val) == 2:
        return f"00{str_val}"
    elif len(str_val) == 3:
        return f"0{str_val}"
    return str_val[:4]

def get_nama_shio(nomor_2d):
    try:
        num = int(nomor_2d)
    except (ValueError, TypeError):
        return "-"
    for shio, angka in DATA_SHIO.items():
        if num in angka:
            return shio
    return "-"

def hitung_selisih(a, b):
    selisih = abs(a - b)
    return selisih if selisih <= 5 else 10 - selisih

def get_kembang_kempis(a, b):
    return "Kembang" if a <= b else "Kempis"

def index_digit(digit):
    return (digit + 4) % 10

def get_angka_main_dari_biji(biji):
    """Rumus angka main berdasarkan biji"""
    step1 = 10 - biji
    if step1 >= 10:
        step1 = step1 % 10
    
    a = step1 % 10
    b = (step1 + 1) % 10
    c = (step1 + 2) % 10
    
    a_idx = index_digit(a)
    b_idx = index_digit(b)
    c_idx = index_digit(c)
    
    return {
        "biji": biji,
        "digits": [a, b, c, a_idx, b_idx, c_idx],
        "rumus": f"{10-biji} → +2 = {a}{b}{c} → index = {a_idx}{b_idx}{c_idx}"
    }

def get_prediksi_dari_2d_belakang(nomor_4d):
    """Dari nomor 4D, ambil 2D belakang, hitung biji, lalu angka main untuk prediksi selanjutnya"""
    if len(str(nomor_4d)) != 4:
        return None
    
    two_d_belakang = int(str(nomor_4d)[2:4])
    a = int(str(nomor_4d)[2])
    b = int(str(nomor_4d)[3])
    
    biji_raw = (a + b) % 9
    biji = 9 if biji_raw == 0 else biji_raw
    
    angka_main = get_angka_main_dari_biji(biji)
    
    return {
        "nomor_sumber": nomor_4d,
        "two_d_belakang": two_d_belakang,
        "a": a,
        "b": b,
        "biji": biji,
        "angka_main_prediksi": angka_main["digits"],
        "rumus": angka_main["rumus"]
    }

def cek_prediksi(prediksi_angka_main, nomor_berikutnya):
    """Cek apakah angka main prediksi muncul di nomor berikutnya"""
    if not prediksi_angka_main or not nomor_berikutnya:
        return False, []
    
    digits_nomor_berikut = [int(d) for d in str(nomor_berikutnya)]
    digit_yang_muncul = [d for d in prediksi_angka_main if d in digits_nomor_berikut]
    
    return len(digit_yang_muncul) > 0, digit_yang_muncul

def generate_rows_for_number(full_number):
    clean_num = str(full_number).replace("-", "").replace(" ", "")
    if len(clean_num) != 4:
        return []
    
    digits = [int(d) for d in clean_num]
    segments = [
        {"label": "Depan", "twoD": clean_num[0:2], "a": digits[0], "b": digits[1]},
        {"label": "Tengah", "twoD": clean_num[1:3], "a": digits[1], "b": digits[2]},
        {"label": "Belakang", "twoD": clean_num[2:4], "a": digits[2], "b": digits[3]}
    ]
    
    rows = []
    for seg in segments:
        two_d_val = int(seg["twoD"])
        is_tengah = 25 <= two_d_val <= 75
        biji_raw = (seg["a"] + seg["b"]) % 9
        biji = 9 if biji_raw == 0 else biji_raw
        shio = get_nama_shio(seg["twoD"])
        kembang_kempis = get_kembang_kempis(seg["a"], seg["b"])
        selisih = hitung_selisih(seg["a"], seg["b"])
        
        rows.append({
            "Nomor 4D": clean_num,
            "Segmen": seg["label"],
            "2D": seg["twoD"],
            "Tengah/Tepi": "Tengah" if is_tengah else "Tepi",
            "Shio": shio,
            "Biji": biji,
            "Bj S": "Genap" if biji % 2 == 0 else "Ganjil",
            "Bj U": "Besar" if biji > 4 else "Kecil",
            "Kp S": "Genap" if seg["a"] % 2 == 0 else "Ganjil",
            "Kp U": "Besar" if seg["a"] > 4 else "Kecil",
            "Ek S": "Genap" if seg["b"] % 2 == 0 else "Ganjil",
            "Ek U": "Besar" if seg["b"] > 4 else "Kecil",
            "S/H": "Silang" if (seg["a"] % 2) != (seg["b"] % 2) else "Homo",
            "K/K": kembang_kempis,
            "Selisih": selisih
        })
    return rows

# ==================== AI PREDIKSI ====================
class AIPrediktor:
    def __init__(self, prediksi_history):
        self.history = prediksi_history
        self.biji_akurasi = self._hitung_akurasi_per_biji()
        self.pola_beruntun = self._deteksi_pola_beruntun()
        self.digit_favorit = self._hitung_digit_favorit()
    
    def _hitung_akurasi_per_biji(self):
        """Hitung akurasi setiap biji dari data historis"""
        biji_stats = {}
        for p in self.history:
            biji = p["biji"]
            if biji not in biji_stats:
                biji_stats[biji] = {"total": 0, "berhasil": 0}
            biji_stats[biji]["total"] += 1
            if p["berhasil"]:
                biji_stats[biji]["berhasil"] += 1
        
        for biji in biji_stats:
            total = biji_stats[biji]["total"]
            berhasil = biji_stats[biji]["berhasil"]
            biji_stats[biji]["akurasi"] = (berhasil / total * 100) if total > 0 else 0
        
        return biji_stats
    
    def _deteksi_pola_beruntun(self):
        """Deteksi pola beruntun (misal: 3x berhasil berturut-turut)"""
        if len(self.history) < 2:
            return []
        
        pola = []
        streak_berhasil = 0
        streak_gagal = 0
        
        for p in self.history[-10:]:  # lihat 10 terakhir
            if p["berhasil"]:
                streak_berhasil += 1
                streak_gagal = 0
            else:
                streak_gagal += 1
                streak_berhasil = 0
            
            pola.append({
                "streak_berhasil": streak_berhasil,
                "streak_gagal": streak_gagal
            })
        
        return pola
    
    def _hitung_digit_favorit(self):
        """Hitung digit yang paling sering muncul dalam prediksi"""
        digit_count = {i: 0 for i in range(10)}
        for p in self.history:
            if p["berhasil"]:
                for digit in p["digit_muncul"]:
                    digit_count[digit] += 1
        return sorted(digit_count.items(), key=lambda x: x[1], reverse=True)
    
    def prediksi_ai(self, nomor_terakhir, jumlah_prediksi=3):
        """Generate AI predictions untuk nomor selanjutnya"""
        prediksi_dasar = get_prediksi_dari_2d_belakang(nomor_terakhir)
        if not prediksi_dasar:
            return []
        
        semua_prediksi = []
        
        # Prediksi 1: Berdasarkan rumus utama (100% based on formula)
        semua_prediksi.append({
            "nama": "RUMUS UTAMA",
            "confidence": 85,
            "angka_main": prediksi_dasar["angka_main_prediksi"],
            "biji": prediksi_dasar["biji"],
            "alasan": f"Rumus dasar dari 2D belakang {prediksi_dasar['two_d_belakang']} (Biji {prediksi_dasar['biji']})"
        })
        
        # Prediksi 2: Berdasarkan biji dengan akurasi tertinggi
        if self.biji_akurasi:
            biji_terbaik = max(self.biji_akurasi.items(), key=lambda x: x[1]["akurasi"])
            if biji_terbaik[1]["total"] >= 2:  # minimal 2 data
                angka_main_biji_terbaik = get_angka_main_dari_biji(biji_terbaik[0])
                semua_prediksi.append({
                    "nama": "BIJI TERBAIK (AI)",
                    "confidence": min(95, biji_terbaik[1]["akurasi"]),
                    "angka_main": angka_main_biji_terbaik["digits"],
                    "biji": biji_terbaik[0],
                    "alasan": f"Biji {biji_terbaik[0]} memiliki akurasi {biji_terbaik[1]['akurasi']:.1f}% dari {biji_terbaik[1]['total']} prediksi"
                })
        
        # Prediksi 3: Kombinasi digit favorit + rumus utama
        if self.digit_favorit:
            digit_favorit_list = [d for d, _ in self.digit_favorit[:3]]
            kombinasi = list(set(prediksi_dasar["angka_main_prediksi"] + digit_favorit_list))[:6]
            semua_prediksi.append({
                "nama": "KOMBINASI AI",
                "confidence": 70,
                "angka_main": kombinasi,
                "biji": prediksi_dasar["biji"],
                "alasan": f"Kombinasi rumus utama + digit favorit: {digit_favorit_list}"
            })
        
        # Prediksi 4: Deteksi pola beruntun
        if len(self.pola_beruntun) >= 2:
            pola_terakhir = self.pola_beruntun[-1]
            if pola_terakhir["streak_berhasil"] >= 2:
                # Lagi panas, pakai biji yang sama
                biji_sama = self.history[-1]["biji"]
                angka_main_sama = get_angka_main_dari_biji(biji_sama)
                semua_prediksi.append({
                    "nama": "HOT STREAK (AI)",
                    "confidence": 80,
                    "angka_main": angka_main_sama["digits"],
                    "biji": biji_sama,
                    "alasan": f"Pola beruntun {pola_terakhir['streak_berhasil']}x berhasil berturut-turut"
                })
            elif pola_terakhir["streak_gagal"] >= 2:
                # Lagi dingin, ganti biji
                biji_alternatif = (self.history[-1]["biji"] % 9) + 1
                angka_main_alternatif = get_angka_main_dari_biji(biji_alternatif)
                semua_prediksi.append({
                    "nama": "COLD BREAK (AI)",
                    "confidence": 65,
                    "angka_main": angka_main_alternatif["digits"],
                    "biji": biji_alternatif,
                    "alasan": f"Pola gagal {pola_terakhir['streak_gagal']}x, mencoba biji alternatif"
                })
        
        # Batasi jumlah prediksi
        return semua_prediksi[:jumlah_prediksi]
    
    def get_rekomendasi_digit(self, nomor_terakhir):
        """Rekomendasi digit berdasarkan AI"""
        prediksi_ai = self.prediksi_ai(nomor_terakhir, 1)
        if prediksi_ai:
            return prediksi_ai[0]["angka_main"]
        return get_prediksi_dari_2d_belakang(nomor_terakhir)["angka_main_prediksi"]
    
    def get_analisis(self):
        """Analisis mendalam dari AI"""
        if len(self.history) < 2:
            return "Data belum cukup untuk analisis AI. Masukkan minimal 2 nomor."
        
        total = len(self.history)
        berhasil = sum(1 for p in self.history if p["berhasil"])
        akurasi = (berhasil / total * 100)
        
        biji_terbaik = max(self.biji_akurasi.items(), key=lambda x: x[1]["akurasi"]) if self.biji_akurasi else (None, None)
        biji_terburuk = min(self.biji_akurasi.items(), key=lambda x: x[1]["akurasi"]) if self.biji_akurasi else (None, None)
        
        analisis = f"""
        📊 **STATISTIK AI:**
        - Total prediksi: {total}
        - Berhasil: {berhasil} ✅
        - Gagal: {total-berhasil} ❌
        - Akurasi keseluruhan: {akurasi:.1f}%
        
        🎯 **PERFORMANCE PER BIJI:**
        """
        
        if biji_terbaik and biji_terbaik[0]:
            analisis += f"\n        - Biji terbaik: {biji_terbaik[0]} (akurasi {biji_terbaik[1]['akurasi']:.1f}%)"
        if biji_terburuk and biji_terburuk[0]:
            analisis += f"\n        - Biji terburuk: {biji_terburuk[0]} (akurasi {biji_terburuk[1]['akurasi']:.1f}%)"
        
        if self.digit_favorit:
            top_digits = [str(d) for d, _ in self.digit_favorit[:3]]
            analisis += f"\n\n🔥 **DIGIT FAVORIT AI:** {', '.join(top_digits)}"
        
        return analisis

# ==================== INISIALISASI SESSION STATE ====================
if "data_store" not in st.session_state:
    st.session_state.data_store = []

if "prediksi_history" not in st.session_state:
    st.session_state.prediksi_history = []

# ==================== CSS CUSTOM ====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #ffffff, #00d4aa);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .success-card {
        background: linear-gradient(135deg, #00d4aa20, #2ecc7120);
        border: 1px solid #00d4aa;
        border-radius: 16px;
        padding: 12px;
        text-align: center;
    }
    .failed-card {
        background: linear-gradient(135deg, #e6394620, #ff6b6b20);
        border: 1px solid #e63946;
        border-radius: 16px;
        padding: 12px;
        text-align: center;
    }
    .ai-card {
        background: linear-gradient(135deg, #7b2ff720, #9b59b620);
        border: 1px solid #9b59b6;
        border-radius: 16px;
        padding: 15px;
    }
    .digit-box {
        display: inline-block;
        width: 42px;
        height: 42px;
        line-height: 42px;
        text-align: center;
        border-radius: 10px;
        margin: 3px;
        font-weight: bold;
        font-size: 18px;
    }
    .digit-box-success {
        background: #2ecc71;
        color: #080b10;
    }
    .digit-box-failed {
        background: #2a3a48;
        color: #5f7f8c;
    }
    .confidence-high {
        color: #2ecc71;
        font-weight: bold;
    }
    .confidence-mid {
        color: #f1c40f;
        font-weight: bold;
    }
    .confidence-low {
        color: #e63946;
        font-weight: bold;
    }
    .stDataFrame {
        border-radius: 20px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown('<h1 class="main-header">🤖 REKAP 4D PRO • AI PREDIKSI</h1>', unsafe_allow_html=True)
with col2:
    st.metric("📊 Total nomor", len(st.session_state.data_store))

# ==================== TAB NAVIGATION ====================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 MASTER DATA", "🤖 AI PREDIKSI", "🔮 VALIDASI", "📊 ANALISIS", "📋 REKAP"])

# ==================== TAB 1: MASTER DATA ====================
with tab1:
    col_input1, col_input2, col_input3 = st.columns([2, 3, 2])
    
    with col_input1:
        st.markdown("### Tambah Nomor")
        nomor_input = st.text_input("Nomor 4D", max_chars=4, placeholder="0000", key="nomor_input")
        if st.button("➕ TAMBAH", use_container_width=True):
            if nomor_input:
                cleaned = nomor_input.strip().replace("-", "").replace(" ", "")
                if len(cleaned) == 4 and cleaned.isdigit():
                    formatted = format_4d(cleaned)
                    if formatted not in st.session_state.data_store:
                        st.session_state.data_store.append(formatted)
                        st.success(f"✅ {formatted} ditambahkan")
                        # Update prediksi history
                        if len(st.session_state.data_store) >= 2:
                            pred = get_prediksi_dari_2d_belakang(st.session_state.data_store[-2])
                            if pred:
                                is_success, muncul = cek_prediksi(pred["angka_main_prediksi"], st.session_state.data_store[-1])
                                st.session_state.prediksi_history.append({
                                    "nomor_sebelum": st.session_state.data_store[-2],
                                    "nomor_sesudah": st.session_state.data_store[-1],
                                    "biji": pred["biji"],
                                    "angka_main_prediksi": pred["angka_main_prediksi"],
                                    "rumus": pred["rumus"],
                                    "berhasil": is_success,
                                    "digit_muncul": muncul
                                })
                        st.rerun()
                    else:
                        st.warning(f"Nomor {formatted} sudah ada!")
                else:
                    st.error("Masukkan 4 digit angka!")
            else:
                st.error("Masukkan nomor 4D!")
    
    with col_input2:
        st.markdown("### Input Massal (Urut Berdasarkan Waktu)")
        st.caption("Masukkan nomor urut dari yang TERLAMA ke TERBARU")
        massal_input = st.text_area("Pisahkan dengan *, |, atau spasi", height=80, placeholder="4324*4366*1234")
        if st.button("📦 PROSES MASSAL", use_container_width=True):
            if massal_input:
                import re
                numbers = re.split(r'[\s*,;\n|*]+', massal_input)
                added = []
                for num in numbers:
                    cleaned = num.strip().replace("-", "").replace(" ", "")
                    if len(cleaned) == 4 and cleaned.isdigit() and cleaned not in st.session_state.data_store:
                        st.session_state.data_store.append(cleaned)
                        added.append(cleaned)
                    elif len(cleaned) == 3 and cleaned.isdigit():
                        formatted = cleaned.zfill(4)
                        if formatted not in st.session_state.data_store:
                            st.session_state.data_store.append(formatted)
                            added.append(formatted)
                if added:
                    st.success(f"✅ +{len(added)} nomor baru ditambahkan")
                    # Generate ulang prediksi history
                    st.session_state.prediksi_history = []
                    for i in range(len(st.session_state.data_store) - 1):
                        pred = get_prediksi_dari_2d_belakang(st.session_state.data_store[i])
                        if pred:
                            is_success, muncul = cek_prediksi(pred["angka_main_prediksi"], st.session_state.data_store[i + 1])
                            st.session_state.prediksi_history.append({
                                "nomor_sebelum": st.session_state.data_store[i],
                                "nomor_sesudah": st.session_state.data_store[i + 1],
                                "biji": pred["biji"],
                                "angka_main_prediksi": pred["angka_main_prediksi"],
                                "rumus": pred["rumus"],
                                "berhasil": is_success,
                                "digit_muncul": muncul
                            })
                    st.rerun()
                else:
                    st.warning("Tidak ada nomor baru yang ditambahkan")
    
    with col_input3:
        st.markdown("### Import/Export")
        uploaded_file = st.file_uploader("📂 IMPORT EXCEL", type=["xlsx", "xls"])
        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file)
            nomor_col = None
            for col in df.columns:
                if 'nomor' in col.lower():
                    nomor_col = col
                    break
            if nomor_col is None:
                nomor_col = df.columns[0]
            
            added = 0
            for val in df[nomor_col].dropna():
                str_val = str(val).strip().replace("-", "").replace(" ", "")
                if len(str_val) == 4 and str_val.isdigit() and str_val not in st.session_state.data_store:
                    st.session_state.data_store.append(str_val)
                    added += 1
                elif len(str_val) == 3 and str_val.isdigit():
                    formatted = str_val.zfill(4)
                    if formatted not in st.session_state.data_store:
                        st.session_state.data_store.append(formatted)
                        added += 1
            if added:
                # Generate ulang prediksi history
                st.session_state.prediksi_history = []
                for i in range(len(st.session_state.data_store) - 1):
                    pred = get_prediksi_dari_2d_belakang(st.session_state.data_store[i])
                    if pred:
                        is_success, muncul = cek_prediksi(pred["angka_main_prediksi"], st.session_state.data_store[i + 1])
                        st.session_state.prediksi_history.append({
                            "nomor_sebelum": st.session_state.data_store[i],
                            "nomor_sesudah": st.session_state.data_store[i + 1],
                            "biji": pred["biji"],
                            "angka_main_prediksi": pred["angka_main_prediksi"],
                            "rumus": pred["rumus"],
                            "berhasil": is_success,
                            "digit_muncul": muncul
                        })
                st.success(f"✅ Import selesai! {added} nomor baru ditambahkan")
                st.rerun()
            else:
                st.info("Tidak ada nomor baru dari file")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📎 EXPORT", use_container_width=True):
                if st.session_state.data_store:
                    all_rows = []
                    for nom in st.session_state.data_store:
                        all_rows.extend(generate_rows_for_number(nom))
                    if all_rows:
                        export_df = pd.DataFrame(all_rows)
                        csv = export_df.to_csv(index=False)
                        st.download_button(
                            label="⬇️ Download CSV",
                            data=csv,
                            file_name=f"Rekap_4D_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                else:
                    st.warning("Tidak ada data untuk diexport")
        with col_btn2:
            if st.button("🗑️ RESET", use_container_width=True):
                st.session_state.data_store = []
                st.session_state.prediksi_history = []
                st.success("Semua data dihapus")
                st.rerun()

# ==================== TAB 2: AI PREDIKSI ====================
with tab2:
    st.markdown("### 🤖 AI PREDICTION ENGINE")
    st.markdown("""
    > AI menganalisis pola historis, akurasi per biji, dan tren untuk memberikan prediksi terbaik.
    > 
    > **Metode AI:** Machine Learning berbasis statistik, deteksi pola beruntun, dan optimasi digit favorit.
    """)
    
    if len(st.session_state.data_store) >= 2:
        # Inisialisasi AI
        ai = AIPrediktor(st.session_state.prediksi_history)
        nomor_terakhir = st.session_state.data_store[-1]
        
        # Tampilkan analisis AI
        with st.expander("📊 ANALISIS AI - Klik untuk lihat detail", expanded=True):
            st.markdown(ai.get_analisis())
        
        st.markdown("---")
        st.markdown("### 🎯 REKOMENDASI PREDIKSI AI")
        
        # Dapatkan prediksi AI
        prediksi_ai = ai.prediksi_ai(nomor_terakhir, 4)
        
        # Tampilkan prediksi dalam grid
        cols = st.columns(2)
        for idx, pred in enumerate(prediksi_ai):
            with cols[idx % 2]:
                # Tentukan class confidence
                if pred["confidence"] >= 80:
                    conf_class = "confidence-high"
                    conf_text = "TINGGI"
                elif pred["confidence"] >= 60:
                    conf_class = "confidence-mid"
                    conf_text = "SEDANG"
                else:
                    conf_class = "confidence-low"
                    conf_text = "RENDAH"
                
                st.markdown(f"""
                <div class="ai-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 18px; font-weight: bold;">🤖 {pred['nama']}</div>
                        <div class="{conf_class}">Confidence: {pred['confidence']:.0f}% ({conf_text})</div>
                    </div>
                    <div style="text-align: center; margin: 15px 0;">
                """, unsafe_allow_html=True)
                
                # Tampilkan digit prediksi
                html_digits = ""
                for digit in pred["angka_main"]:
                    html_digits += f'<span class="digit-box" style="background:#9b59b6; color:white;">{digit}</span>'
                st.markdown(html_digits, unsafe_allow_html=True)
                
                st.markdown(f"""
                    </div>
                    <div style="font-size: 12px; color: #aaa; text-align: center;">
                        Biji: {pred['biji']} | {pred['alasan']}
                    </div>
                </div>
                <br>
                """, unsafe_allow_html=True)
        
        # Rekomendasi final AI
        st.markdown("---")
        st.markdown("### ⭐ REKOMENDASI FINAL AI")
        
        final_rekom = ai.get_rekomendasi_digit(nomor_terakhir)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #9b59b6, #7b2ff7); border-radius: 20px; padding: 20px; text-align: center;">
                <div style="font-size: 14px; opacity: 0.8;">🎯 AI PREDIKSI UNTUK KELUARAN BERIKUTNYA</div>
                <div style="font-size: 12px; margin-top: 5px;">Berdasarkan {len(st.session_state.prediksi_history)} data historis</div>
                <div style="margin: 15px 0;">
            """, unsafe_allow_html=True)
            
            html_digits = ""
            for digit in final_rekom:
                html_digits += f'<span class="digit-box" style="background:white; color:#7b2ff7; width: 50px; height: 50px; line-height: 50px; font-size: 22px;">{digit}</span>'
            st.markdown(html_digits, unsafe_allow_html=True)
            
            st.markdown(f"""
                </div>
                <div style="font-size: 11px;">
                    Dari nomor terakhir: {nomor_terakhir} (2D belakang: {str(nomor_terakhir)[2:4]})
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Informasi update
        st.info("💡 **Tips:** Gunakan prediksi AI sebagai referensi. Semakin banyak data historis, semakin akurat prediksi AI.")
        
    else:
        st.warning("⚠️ Minimal 2 nomor untuk AI Prediksi. Masukkan data di Tab MASTER DATA.")

# ==================== TAB 3: VALIDASI ====================
with tab3:
    st.markdown("### 🔮 VALIDASI PREDIKSI")
    st.markdown("""
    > Setiap prediksi berdasarkan 2D belakang dari nomor sebelumnya divalidasi otomatis.
    > ✅ = Angka main prediksi muncul di nomor target | ❌ = Tidak muncul sama sekali
    """)
    
    if len(st.session_state.data_store) >= 2:
        # Statistik ringkasan
        total_prediksi = len(st.session_state.prediksi_history)
        berhasil_count = sum(1 for p in st.session_state.prediksi_history if p["berhasil"])
        gagal_count = total_prediksi - berhasil_count
        persen_berhasil = (berhasil_count / total_prediksi * 100) if total_prediksi > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Prediksi", total_prediksi)
        with col2:
            st.metric("✅ BERHASIL", berhasil_count, delta=f"{persen_berhasil:.1f}%")
        with col3:
            st.metric("❌ GAGAL", gagal_count)
        with col4:
            st.metric("🎯 Akurasi", f"{persen_berhasil:.1f}%")
        
        st.progress(persen_berhasil / 100)
        
        # Tabel riwayat prediksi
        st.markdown("### 📋 RIWAYAT PREDIKSI")
        
        history_rows = []
        for idx, h in enumerate(st.session_state.prediksi_history):
            prediksi_str = " | ".join(map(str, h["angka_main_prediksi"]))
            digit_muncul_str = ", ".join(map(str, h["digit_muncul"])) if h["digit_muncul"] else "-"
            
            history_rows.append({
                "No": idx + 1,
                "Nomor Sebelum": h["nomor_sebelum"],
                "2D Belakang": str(h["nomor_sebelum"])[2:4],
                "Biji": h["biji"],
                "Nomor Sesudah": h["nomor_sesudah"],
                "Angka Main Prediksi": prediksi_str,
                "Digit Yang Muncul": digit_muncul_str,
                "Status": "✅ BERHASIL" if h["berhasil"] else "❌ GAGAL"
            })
        
        df_history = pd.DataFrame(history_rows)
        st.dataframe(df_history, use_container_width=True, hide_index=True)
        
        # Detail per prediksi dengan visualisasi
        st.markdown("### 🔍 DETAIL SETIAP PREDIKSI")
        
        for idx, h in enumerate(st.session_state.prediksi_history[-5:]):  # 5 terakhir
            status_color = "#00d4aa" if h["berhasil"] else "#e63946"
            status_text = "BERHASIL ✓" if h["berhasil"] else "GAGAL ✗"
            
            with st.expander(f"{'✅' if h['berhasil'] else '❌'} Prediksi #{len(st.session_state.prediksi_history)-idx}: {h['nomor_sebelum']} → {h['nomor_sesudah']}", expanded=False):
                cols = st.columns([1, 2])
                
                with cols[0]:
                    st.markdown(f"""
                    <div style="background:#0e1318; border-radius:16px; padding:15px;">
                        <div style="text-align:center;">
                            <div style="font-size:12px; color:#5f7f8c;">Nomor Sumber</div>
                            <div style="font-size:28px; font-weight:bold;">{h['nomor_sebelum']}</div>
                            <div style="font-size:14px; color:#00d4aa;">2D Belakang: {str(h['nomor_sebelum'])[2:4]}</div>
                            <div style="font-size:14px;">Biji: {h['biji']}</div>
                            <hr style="margin:10px 0;">
                            <div style="font-size:12px; color:#5f7f8c;">Nomor Target</div>
                            <div style="font-size:28px; font-weight:bold;">{h['nomor_sesudah']}</div>
                            <hr style="margin:10px 0;">
                            <div style="font-size:12px; color:#5f7f8c;">Status</div>
                            <div style="font-size:20px; font-weight:bold; color:{status_color};">{status_text}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[1]:
                    st.markdown(f"""
                    <div style="background:#0e1318; border-radius:16px; padding:15px;">
                        <div style="text-align:center; margin-bottom:10px; font-weight:bold;">ANGKA MAIN PREDIKSI</div>
                        <div style="text-align:center;">
                    """, unsafe_allow_html=True)
                    
                    html_digits = ""
                    for digit in h["angka_main_prediksi"]:
                        is_muncul = digit in h["digit_muncul"]
                        bg = "#2ecc71" if is_muncul else "#2a3a48"
                        color = "#080b10" if is_muncul else "#5f7f8c"
                        html_digits += f'<span class="digit-box" style="background:{bg}; color:{color};">{digit}</span>'
                    
                    st.markdown(html_digits, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        </div>
                        <div style="margin-top:15px; font-size:12px; color:#5f7f8c; text-align:center;">
                            Rumus: {h['rumus']}
                        </div>
                        <div style="margin-top:10px; text-align:center;">
                            {'✅ Digit ' + ', '.join(map(str, h['digit_muncul'])) + ' muncul di nomor target' if h['digit_muncul'] else '❌ Tidak ada digit prediksi yang muncul'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Prediksi untuk keluaran selanjutnya
        st.markdown("---")
        st.markdown("### ⏳ PREDIKSI DARI NOMOR TERAKHIR")
        
        nomor_terakhir = st.session_state.data_store[-1]
        prediksi_terakhir = get_prediksi_dari_2d_belakang(nomor_terakhir)
        
        if prediksi_terakhir:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown(f"""
                <div style="background:#0e1318; border-radius:16px; padding:20px; text-align:center; border:1px solid #00d4aa;">
                    <div style="font-size:14px; color:#5f7f8c;">Nomor Terakhir</div>
                    <div style="font-size:36px; font-weight:bold;">{nomor_terakhir}</div>
                    <div style="font-size:14px;">2D Belakang: {str(nomor_terakhir)[2:4]}</div>
                    <div style="font-size:14px;">Biji: {prediksi_terakhir['biji']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background:#0e1318; border-radius:16px; padding:20px; text-align:center; border:1px solid #00d4aa;">
                    <div style="font-size:14px; color:#5f7f8c;">ANGKA MAIN PREDIKSI</div>
                    <div style="margin:10px 0;">
                """, unsafe_allow_html=True)
                
                html_digits = ""
                for digit in prediksi_terakhir["angka_main_prediksi"]:
                    html_digits += f'<span class="digit-box" style="background:#2a3a48; color:#5f7f8c;">{digit}</span>'
                st.markdown(html_digits, unsafe_allow_html=True)
                
                st.markdown(f"""
                    </div>
                    <div style="font-size:11px; color:#5f7f8c;">Rumus: {prediksi_terakhir['rumus']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.info("💡 **Tips:** Tunggu hasil undian berikutnya untuk memvalidasi prediksi di atas.")
    
    else:
        st.warning("⚠️ Minimal 2 nomor untuk validasi prediksi. Masukkan data di Tab MASTER DATA.")

# ==================== TAB 4: ANALISIS ====================
with tab4:
    if st.session_state.prediksi_history:
        st.markdown("### 📊 ANALISIS STATISTIK")
        
        # Kelompokkan berdasarkan biji
        biji_stats = {}
        for p in st.session_state.prediksi_history:
            biji = p["biji"]
            if biji not in biji_stats:
                biji_stats[biji] = {"total": 0, "berhasil": 0}
            biji_stats[biji]["total"] += 1
            if p["berhasil"]:
                biji_stats[biji]["berhasil"] += 1
        
        # Tampilkan tabel per biji
        biji_rows = []
        for biji in range(1, 10):
            if biji in biji_stats:
                total = biji_stats[biji]["total"]
                berhasil = biji_stats[biji]["berhasil"]
                persen = (berhasil / total * 100) if total > 0 else 0
            else:
                total = 0
                berhasil = 0
                persen = 0
            
            biji_rows.append({
                "Biji": biji,
                "Jumlah Prediksi": total,
                "Berhasil": berhasil,
                "Gagal": total - berhasil,
                "Akurasi": f"{persen:.1f}%"
            })
        
        df_biji_stats = pd.DataFrame(biji_rows)
        
        # Warna berdasarkan akurasi
        def color_accuracy(val):
            try:
                angka = float(val.replace("%", ""))
                if angka >= 70:
                    return "color: #2ecc71; font-weight: bold"
                elif angka >= 40:
                    return "color: #f1c40f"
                else:
                    return "color: #e63946"
            except:
                return ""
        
        st.dataframe(df_biji_stats.style.applymap(color_accuracy, subset=["Akurasi"]), use_container_width=True, hide_index=True)
        
        # Chart akurasi per biji
        fig = px.bar(
            x=[b for b in range(1, 10)],
            y=[float(df_biji_stats[df_biji_stats["Biji"] == b]["Akurasi"].values[0].replace("%", "")) if len(df_biji_stats[df_biji_stats["Biji"] == b]) > 0 else 0 for b in range(1, 10)],
            labels={"x": "Biji", "y": "Akurasi (%)"},
            title="Akurasi Prediksi per Biji"
        )
        fig.update_layout(plot_bgcolor="#0e1318", paper_bgcolor="#0e1318", font_color="#d0e8f0")
        fig.update_traces(marker_color="#00d4aa")
        st.plotly_chart(fig, use_container_width=True)
        
        # Top digit
        st.markdown("### 🔥 DIGIT PALING SERING MUNCUL DALAM PREDIKSI")
        
        semua_digit = {i: 0 for i in range(10)}
        for p in st.session_state.prediksi_history:
            if p["berhasil"]:
                for digit in p["digit_muncul"]:
                    semua_digit[digit] += 1
        
        sorted_digits = sorted(semua_digit.items(), key=lambda x: x[1], reverse=True)[:5]
        cols = st.columns(5)
        for i, (digit, freq) in enumerate(sorted_digits):
            with cols[i]:
                st.markdown(f"""
                <div style="background:#0e1318; border-radius:16px; padding:12px; text-align:center;">
                    <div style="font-size:32px; font-weight:bold; color:#00d4aa;">{digit}</div>
                    <div>{freq}x kemunculan</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Tren prediksi
        st.markdown("### 📈 TREN PREDIKSI (10 TERAKHIR)")
        
        tren_data = []
        for idx, p in enumerate(st.session_state.prediksi_history[-10:]):
            tren_data.append({
                "Ke-": idx + 1,
                "Status": 1 if p["berhasil"] else 0,
                "Biji": p["biji"]
            })
        
        df_tren = pd.DataFrame(tren_data)
        fig = px.line(df_tren, x="Ke-", y="Status", markers=True, title="Tren Keberhasilan Prediksi (1=Berhasil, 0=Gagal)")
        fig.update_layout(plot_bgcolor="#0e1318", paper_bgcolor="#0e1318", font_color="#d0e8f0")
        fig.update_traces(line_color="#2ecc71", marker_color="#00d4aa")
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("📊 Belum ada data prediksi. Masukkan minimal 2 nomor di Tab MASTER DATA.")

# ==================== TAB 5: REKAP ====================
with tab5:
    st.markdown("### 📋 TABEL REKAP DATA LENGKAP")
    
    if st.session_state.data_store:
        all_rows = []
        for nom in st.session_state.data_store:
            all_rows.extend(generate_rows_for_number(nom))
        
        if all_rows:
            df_display = pd.DataFrame(all_rows)
            st.dataframe(df_display, use_container_width=True, height=400)
    else:
        st.info("✨ Masukkan nomor 4D atau import Excel ✨")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown(
    '<p style="text-align: center; font-size: 11px; opacity: 0.6;">🤖 AI Prediksi berdasarkan analisis data historis. Semakin banyak data, semakin akurat prediksi.</p>',
    unsafe_allow_html=True
)