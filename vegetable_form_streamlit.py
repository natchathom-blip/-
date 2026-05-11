import streamlit as st
import pandas as pd
import os
from fpdf import FPDF

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CPRAM Supplier Form", layout="wide")

# --- 2. ฟังก์ชันโหลดข้อมูลที่อยู่ (ใช้ชื่อไฟล์ตรงตาม GitHub: thailand.xlsx) ---
@st.cache_data
def load_address_data():
    file_path = 'thailand.xlsx' #
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path) #
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

df_addr = load_address_data()

# --- 3. ส่วนหัวกระดาษ (Header) ---
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; margin-bottom: 20px;">
        <div style="background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 26px;">cpram</div>
        <div style="text-align: right;"><b>FR-QAS-10-000</b><br><small>มีผลใช้งาน: 2026-05-08</small></div>
    </div>
    """, unsafe_allow_html=True) #

st.subheader("แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด") # 

# --- 4. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ (Lock ข้อมูล) ---
st.markdown("#### ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ")
c1, c2, c3 = st.columns(3)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name") # [cite: 2, 3]
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="s_date") # [cite: 4, 5]
s_time = c3.text_input("เวลาส่ง (น.)", key="s_time")

c4, c5 = st.columns(2)
recorder = c4.text_input("ลงชื่อผู้กรอก", key="recorder") # [cite: 27]
origin_main = c5.selectbox("ประเทศแหล่งปลูกหลัก *", ["ประเทศไทย", "จีน", "อื่นๆ"], key="origin_main")

# --- 5. ส่วนที่ 2 — รายการวัตถุดิบ (ดึงข้อมูลกลับมาครบทุกฟิลด์) ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

for i in range(st.session_state.items_count):
    with st.container():
        st.markdown(f'<div style="background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 15px;">', unsafe_allow_html=True)
        st.write(f"**รายการที่ {i+1}**")
        
        # ข้อมูลสินค้า [cite: 6-12]
        r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
        r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}") # [cite: 7]
        r1c2.text_input("Code", key=f"code_{i}") # [cite: 8]
        r1c3.number_input("จำนวน (KG)", min_value=0.0, key=f"qty_{i}") # [cite: 9]

        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.text_input("สายพันธุ์", key=f"breed_{i}") # [cite: 10]
        r2c2.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}") # [cite: 11]
        r2c3.selectbox("ระบบการปลูก", ["- เลือก -", "โรงเรือน/ระบบปิด", "แปลงเปิด/ระบบเปิด"], key=f"sys_{i}") # [cite: 12]

        # วันเวลา [cite: 13-20]
        r3c1, r3c2, r3c3, r3c4 = st.columns(4)
        r3c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}") # [cite: 14]
        r3c2.text_input("เวลาเก็บเกี่ยว", key=f"ht_{i}") # [cite: 16]
        r3c3.date_input("วันที่ล้าง/ตัดแต่ง", key=f"cd_{i}") # [cite: 18]
        r3c4.text_input("เวลาล้าง/ตัดแต่ง", key=f"ct_{i}") # [cite: 20]

        # ข้อมูลผู้ปลูก [cite: 21-25]
        r4c1, r4c2, r4c3 = st.columns(3)
        r4c1.text_input("ชื่อผู้ปลูก", key=f"grower_{i}") # [cite: 22]
        r4c2.text_input("เลขที่ GAP", key=f"gap_{i}") # [cite: 24]
        r4c3.text_input("รหัสไร่", key=f"farm_{i}") # [cite: 25]

        # ที่อยู่ (ล็อกค่า index ไม่ให้หาย)
        st.markdown("📍 **ที่อยู่แหล่งปลูก**")
        if origin_main == "ประเทศไทย" and not df_addr.empty:
            a1, a2, a3 = st.columns(3)
            p_list = sorted(df_addr["จังหวัด"].unique().tolist())
            p_val = a1.selectbox("จังหวัด", ["- เลือก -"] + p_list, key=f"p_{i}")
            
            d_list = sorted(df_addr[df_addr["จังหวัด"] == p_val]["อำเภอ"].unique().tolist()) if p_val != "- เลือก -" else []
            a_val = a2.selectbox("อำเภอ", ["- เลือก -"] + d_list, key=f"a_{i}")
            
            t_list = sorted(df_addr[(df_addr["จังหวัด"] == p_val) & (df_addr["อำเภอ"] == a_val)]["ตำบล"].unique().tolist()) if a_val != "- เลือก -" else []
            t_val = a3.selectbox("ตำบล", ["- เลือก -"] + t_list, key=f"t_{i}")
        else:
            a1, a2, a3 = st.columns(3)
            a1.text_input("จังหวัด", key=f"p_man_{i}")
            a2.text_input("อำเภอ", key=f"a_man_{i}")
            a3.text_input("ตำบล", key=f"t_man_{i}")
        st.markdown('</div>', unsafe_allow_html=True)

if st.button("+ เพิ่มรายการ"):
    st.session_state.items_count += 1
    st.rerun()

# --- 6. สร้าง PDF (ป้องกัน Unicode Error) ---
if st.button("✅ ยืนยันและดาวน์โหลด PDF", type="primary", use_container_width=True):
    pdf = FPDF()
    pdf.add_page()
    font_p = "Sarabun-Regular.ttf" #
    if os.path.exists(font_p):
        pdf.add_font('Sarabun', '', font_p, uni=True)
        pdf.set_font('Sarabun', '', 14)
        
        # เขียน Header ใน PDF
        pdf.cell(0, 10, f"ผู้ส่งมอบ: {st.session_state.s_name}", ln=True)
        pdf.cell(0, 10, f"วันที่ส่ง: {st.session_state.s_date}", ln=True)
        
        for i in range(st.session_state.items_count):
            pdf.ln(5)
            pdf.cell(0, 10, f"รายการที่ {i+1}: {st.session_state.get(f'mat_{i}')} | {st.session_state.get(f'qty_{i}')} KG", ln=True)
            pdf.cell(0, 10, f"ที่อยู่: {st.session_state.get(f'p_{i}')} {st.session_state.get(f'a_{i}')} {st.session_state.get(f't_{i}')}", ln=True)
        
        pdf_out = pdf.output(dest='S').encode('latin-1', 'replace')
        st.download_button("📥 โหลดไฟล์ PDF", data=pdf_out, file_name="CPRAM_Form.pdf")
    else:
        st.error("ไม่พบไฟล์ฟอนต์ Sarabun-Regular.ttf")
