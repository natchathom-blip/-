import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

# --- 1. ฟังก์ชันโหลดข้อมูลที่อยู่ (ปรับปรุงให้ค้นหาไฟล์อัตโนมัติ) ---
@st.cache_data
def load_address_data():
    # รายชื่อไฟล์ที่อาจเป็นไปได้
    possible_files = [
        'thailand.xlsx - Sheet1.csv', 
        'thailand.csv', 
        'thailand.xlsx',
        'thailand_data.csv'
    ]
    
    found_file = None
    for f in possible_files:
        if os.path.exists(f):
            found_file = f
            break
            
    if found_file:
        try:
            if found_file.endswith('.csv'):
                # ลองอ่านแบบ UTF-8 ถ้าพังให้ลองใช้ cp1252 หรือ tis-620
                try:
                    df = pd.read_csv(found_file, encoding='utf-8')
                except:
                    df = pd.read_csv(found_file, encoding='tis-620')
            else:
                df = pd.read_excel(found_file)
            
            # ล้างช่องว่างที่หัวตาราง
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"พบไฟล์ {found_file} แต่เปิดไม่ได้: {e}")
            return pd.DataFrame()
    else:
        # ถ้าไม่เจอเลย ให้แสดงปุ่ม Upload แก้ขัด
        st.warning("⚠️ ไม่พบไฟล์ฐานข้อมูลที่อยู่ (thailand.csv)")
        uploaded_file = st.file_uploader("กรุณาอัปโหลดไฟล์ที่อยู่ (CSV/XLSX)", type=['csv', 'xlsx'])
        if uploaded_file:
            if uploaded_file.name.endswith('.csv'):
                return pd.read_csv(uploaded_file)
            else:
                return pd.read_excel(uploaded_file)
        return pd.DataFrame()

df_addr = load_address_data()

# --- 2. ตั้งค่าหน้าจอและหัวกระดาษ ---
st.set_page_config(page_title="CPRAM Supplier Form", layout="wide")

st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; margin-bottom: 20px;">
        <div style="background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 26px;">cpram</div>
        <div style="text-align: right;"><b>FR-QAS-10-000</b><br><small>มีผลใช้งาน: 2026-05-08</small></div>
    </div>
    """, unsafe_allow_html=True)

# --- 3. ส่วนข้อมูลผู้ส่งมอบ (Lock ข้อมูล) ---
st.subheader("ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ")
c1, c2 = st.columns(2)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="s_date")
origin_main = st.selectbox("ประเทศแหล่งปลูกหลัก", ["ประเทศไทย", "จีน", "อื่นๆ"], key="origin_main")

# --- 4. รายการวัตถุดิบ ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

for i in range(st.session_state.items_count):
    with st.container():
        st.markdown(f'<div style="background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 15px;">', unsafe_allow_html=True)
        st.markdown(f"**รายการที่ {i+1}**")
        
        r1, r2, r3 = st.columns([2, 1, 1])
        mat = r1.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        qty = r3.number_input("จำนวน (KG)", key=f"qty_{i}", min_value=0.0)

        # ส่วน Dropdown ที่อยู่ (แก้ปัญหาหาย)
        st.markdown("📍 **ที่อยู่แหล่งปลูก**")
        if origin_main == "ประเทศไทย" and not df_addr.empty:
            a1, a2, a3 = st.columns(3)
            # จังหวัด
            prov_list = sorted(df_addr["จังหวัด"].unique().tolist())
            p_val = a1.selectbox("จังหวัด", ["- เลือก -"] + prov_list, key=f"p_{i}")
            
            # อำเภอ
            dist_opts = sorted(df_addr[df_addr["จังหวัด"] == p_val]["อำเภอ"].unique().tolist()) if p_val != "- เลือก -" else []
            a_val = a2.selectbox("อำเภอ", ["- เลือก -"] + dist_opts, key=f"a_{i}")
            
            # ตำบล
            sub_opts = sorted(df_addr[(df_addr["จังหวัด"] == p_val) & (df_addr["อำเภอ"] == a_val)]["ตำบล"].unique().tolist()) if a_val != "- เลือก -" else []
            t_val = a3.selectbox("ตำบล", ["- เลือก -"] + sub_opts, key=f"t_{i}")
        else:
            a1, a2, a3 = st.columns(3)
            a1.text_input("จังหวัด/มณฑล", key=f"p_man_{i}")
            a2.text_input("อำเภอ/เมือง", key=f"a_man_{i}")
            a3.text_input("ตำบล/แขวง", key=f"t_man_{i}")

        st.markdown('</div>', unsafe_allow_html=True)

if st.button("+ เพิ่มรายการวัตถุดิบ"):
    st.session_state.items_count += 1
    st.rerun()

# --- 5. ปุ่มยืนยันและสร้าง PDF ---
st.write("---")
if st.button("✅ ยืนยันข้อมูลและดาวน์โหลด PDF", type="primary", use_container_width=True):
    # ตรวจสอบชื่อฟอนต์ในเครื่องคุณ (Sarabun-Regular.ttf)
    font_path = "Sarabun-Regular.ttf"
    
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists(font_path):
        pdf.add_font('Sarabun', '', font_path)
        pdf.set_font('Sarabun', '', 16)
        
        pdf.cell(200, 10, txt="แบบบันทึกผู้ส่งมอบ CPRAM", ln=True, align='C')
        pdf.set_font('Sarabun', '', 12)
        pdf.cell(0, 10, txt=f"ผู้ส่งมอบ: {s_name}", ln=True)
        pdf.cell(0, 10, txt=f"วันที่: {s_date}", ln=True)
        
        pdf_data = pdf.output()
        st.download_button("📥 คลิกดาวน์โหลด PDF", data=bytes(pdf_data), file_name=f"CPRAM_{s_name}.pdf")
    else:
        st.error(f"หาไฟล์ฟอนต์ {font_path} ไม่เจอ")
