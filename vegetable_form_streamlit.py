import streamlit as st
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CPRAM Supplier Form", layout="wide")

# --- 2. ฟังก์ชันโหลดข้อมูลที่อยู่ (ป้องกัน Error ไฟล์หาย) ---
@st.cache_data
def load_address_data():
    file_path = 'thailand.xlsx - Sheet1.csv'
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

df_addr = load_address_data()

# --- 3. ส่วนหัว (Header) ---
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; margin-bottom: 20px;">
        <div style="background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 26px;">cpram</div>
        <div style="text-align: right;"><b>FR-QAS-10-000</b><br><small>มีผลใช้งาน: 2026-05-08</small></div>
    </div>
    """, unsafe_allow_html=True)

# --- 4. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ (Lock ข้อมูลไว้ใน Session State) ---
st.markdown('<p style="color: #2e7d32; font-size: 20px; font-weight: bold;">ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ</p>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="s_date")
s_time = c3.text_input("เวลาส่ง (น.)", placeholder="เช่น 14:00", key="s_time")

c4, c5, c6 = st.columns(3)
s_email = c4.text_input("อีเมลสำหรับรับ PDF *", key="s_email")
recorder = c5.text_input("ลงชื่อผู้กรอก", key="recorder")
origin_main = c6.selectbox("ประเทศแหล่งปลูกหลัก *", ["ประเทศไทย", "จีน", "อื่นๆ"], key="origin_main")

if origin_main == "อื่นๆ":
    origin_other = st.text_input("ระบุชื่อประเทศ *", key="origin_other")
else:
    origin_other = ""

# --- 5. ส่วนที่ 2 — รายการวัตถุดิบ (ระบบ Lock ข้อมูลไม่ให้หาย) ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

def add_item():
    st.session_state.items_count += 1

st.markdown('<p style="color: #2e7d32; font-size: 20px; font-weight: bold;">ส่วนที่ 2 — รายการวัตถุดิบ</p>', unsafe_allow_html=True)

for i in range(st.session_state.items_count):
    with st.container():
        st.markdown(f'<div style="background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 15px;">', unsafe_allow_html=True)
        
        col_h, col_del = st.columns([0.8, 0.2])
        col_h.subheader(f"รายการที่ {i+1}")
        if st.session_state.items_count > 1 and col_del.button(f"✕ ลบรายการนี้", key=f"del_{i}"):
            st.session_state.items_count -= 1
            st.rerun()

        # แถวข้อมูลวัตถุดิบ
        r1, r2, r3 = st.columns([2, 1, 1])
        r1.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        r2.text_input("Code", key=f"code_{i}")
        r3.number_input("จำนวน (KG) *", min_value=0.0, key=f"qty_{i}")

        # วันเวลาที่เก็บเกี่ยว/ล้าง (เพิ่มฟิลด์ตามรูปภาพล่าสุด)
        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.date_input("วันที่เก็บเกี่ยว", key=f"h_date_{i}")
        r2c2.text_input("เวลาเก็บเกี่ยว", key=f"h_time_{i}")
        r2c3.date_input("วันที่ล้างทำความสะอาด", key=f"c_date_{i}")

        # ที่อยู่แหล่งปลูก
        st.markdown(f"📍 **ที่อยู่แหล่งปลูก ({origin_main})**")
        if origin_main == "ประเทศไทย" and not df_addr.empty:
            a1, a2, a3 = st.columns(3)
            p_list = sorted(df_addr["จังหวัด"].unique())
            sel_p = a1.selectbox("จังหวัด", ["- เลือก -"] + p_list, key=f"p_{i}")
            
            amp_opts = sorted(df_addr[df_addr["จังหวัด"] == sel_p]["อำเภอ"].unique()) if sel_p != "- เลือก -" else []
            sel_a = a2.selectbox("อำเภอ", ["- เลือก -"] + amp_opts, key=f"a_{i}")
            
            tam_opts = sorted(df_addr[(df_addr["จังหวัด"] == sel_p) & (df_addr["อำเภอ"] == sel_a)]["ตำบล"].unique()) if sel_a != "- เลือก -" else []
            sel_t = a3.selectbox("ตำบล", ["- เลือก -"] + tam_opts, key=f"t_{i}")
        else:
            a1, a2, a3 = st.columns(3)
            a1.text_input("จังหวัด/มณฑล", key=f"p_man_{i}")
            a2.text_input("อำเภอ/เมือง", key=f"a_man_{i}")
            a3.text_input("ตำบล/แขวง", key=f"t_man_{i}")

        # ลักษณะการปลูก
        r4c1, r4c2, r4c3 = st.columns(3)
        r4c1.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
        r4c2.selectbox("ลักษณะสถานที่ปลูก", ["- เลือก -", "โรงเรือน", "แปลงเปิด"], key=f"loc_{i}")
        r4c3.text_input("สายพันธุ์", key=f"breed_{i}")

        st.markdown('</div>', unsafe_allow_html=True)

st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item)

# --- 6. ปุ่มยืนยันและสร้าง PDF ---
st.write("---")
if st.button("✅ ยืนยันข้อมูลและรับไฟล์ PDF", type="primary", use_container_width=True):
    if not s_name or not s_email:
        st.error("กรุณากรอกชื่อผู้ส่งมอบและอีเมลให้เรียบร้อย")
    else:
        # สร้าง PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="CPRAM - Supplier Record", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Supplier: {s_name}", ln=True)
        pdf.cell(200, 10, txt=f"Email: {s_email}", ln=True)
        pdf.cell(200, 10, txt=f"Date: {s_date}", ln=True)
        
        # บันทึกเป็น PDF bytes
        pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='ignore')
        
        st.success("บันทึกข้อมูลและสร้าง PDF สำเร็จ!")
        st.download_button(
            label="📥 คลิกที่นี่เพื่อดาวน์โหลด PDF",
            data=pdf_bytes,
            file_name=f"CPRAM_{s_name}_{datetime.now().strftime('%d%m%y')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
