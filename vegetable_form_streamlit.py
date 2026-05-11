import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CPRAM Supplier Form", layout="wide")

# --- 2. โหลดข้อมูลที่อยู่ (Dropdown จังหวัด/อำเภอ/ตำบล) ---
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

# --- 4. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ (Lock ข้อมูล) ---
st.subheader("ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ")
c1, c2, c3 = st.columns(3)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="s_date")
s_time = c3.text_input("เวลาส่ง (น.)", placeholder="14:00", key="s_time")

c4, c5, c6 = st.columns(3)
s_email = c4.text_input("อีเมลสำหรับรับ PDF *", key="s_email")
recorder = c5.text_input("ลงชื่อผู้กรอก", key="recorder")
origin_main = c6.selectbox("ประเทศแหล่งปลูกหลัก", ["ประเทศไทย", "จีน", "อื่นๆ"], key="origin_main")

# --- 5. ส่วนที่ 2 — รายการวัตถุดิบ (ข้อมูลไม่หายด้วย Session State) ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

def add_item():
    st.session_state.items_count += 1

st.subheader("ส่วนที่ 2 — รายการวัตถุดิบ")

for i in range(st.session_state.items_count):
    with st.container():
        st.markdown(f'<div style="background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 15px;">', unsafe_allow_html=True)
        
        col_h, col_del = st.columns([0.8, 0.2])
        col_h.markdown(f"**รายการที่ {i+1}**")
        if st.session_state.items_count > 1 and col_del.button(f"✕ ลบรายการ", key=f"del_{i}"):
            st.session_state.items_count -= 1
            st.rerun()

        r1, r2, r3 = st.columns([2, 1, 1])
        r1.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        r2.text_input("Code", key=f"code_{i}")
        r3.number_input("จำนวน (KG)", key=f"qty_{i}", min_value=0.0)

        # จัดการที่อยู่ (Lock ข้อมูลอัตโนมัติ)
        st.markdown(f"📍 **ที่อยู่แหล่งปลูก ({origin_main})**")
        if origin_main == "ประเทศไทย" and not df_addr.empty:
            a1, a2, a3 = st.columns(3)
            p = a1.selectbox("จังหวัด", ["- เลือก -"] + sorted(df_addr["จังหวัด"].unique().tolist()), key=f"p_{i}")
            a = a2.selectbox("อำเภอ", ["- เลือก -"] + sorted(df_addr[df_addr["จังหวัด"] == p]["อำเภอ"].unique().tolist()) if p != "- เลือก -" else [], key=f"a_{i}")
            t = a3.selectbox("ตำบล", ["- เลือก -"] + sorted(df_addr[(df_addr["จังหวัด"] == p) & (df_addr["อำเภอ"] == a)]["ตำบล"].unique().tolist()) if a != "- เลือก -" else [], key=f"t_{i}")
        else:
            a1, a2, a3 = st.columns(3)
            a1.text_input("จังหวัด/มณฑล", key=f"p_man_{i}")
            a2.text_input("อำเภอ/เมือง", key=f"a_man_{i}")
            a3.text_input("ตำบล/แขวง", key=f"t_man_{i}")

        r4c1, r4c2, r4c3 = st.columns(3)
        r4c1.selectbox("ลักษณะการปลูก", ["ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
        r4c2.selectbox("ลักษณะสถานที่ปลูก", ["โรงเรือน", "แปลงเปิด"], key=f"loc_{i}")
        r4c3.text_input("สายพันธุ์", key=f"breed_{i}")

        st.markdown('</div>', unsafe_allow_html=True)

st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item)

# --- 6. ฟังก์ชันสร้าง PDF (ใช้ Sarabun-Regular.ttf) ---
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    font_path = "Sarabun-Regular.ttf" # ชื่อไฟล์ตามที่คุณแจ้ง
    
    if os.path.exists(font_path):
        pdf.add_font('Sarabun', '', font_path)
        pdf.set_font('Sarabun', '', 16)
    else:
        st.error(f"❌ ไม่พบไฟล์ฟอนต์ {font_path} ในระบบ กรุณาตรวจสอบชื่อไฟล์")
        pdf.set_font('Arial', '', 12)

    # เขียนเนื้อหาภาษาไทย
    pdf.cell(200, 10, txt="แบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ (CPRAM)", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"ผู้ส่งมอบ: {st.session_state.s_name}", ln=True)
    pdf.cell(200, 10, txt=f"วันที่ส่ง: {st.session_state.s_date} | ผู้กรอก: {st.session_state.recorder}", ln=True)
    pdf.ln(5)
    
    for i in range(st.session_state.items_count):
        mat = st.session_state.get(f"mat_{i}", "")
        qty = st.session_state.get(f"qty_{i}", 0)
        pdf.cell(200, 10, txt=f"รายการที่ {i+1}: {mat} จำนวน {qty} KG", ln=True)

    return pdf.output()

# --- 7. ปุ่มยืนยันและดาวน์โหลด ---
st.write("---")
if st.button("✅ ยืนยันข้อมูลและดาวน์โหลด PDF", type="primary", use_container_width=True):
    if not s_name:
        st.error("กรุณากรอกชื่อผู้ส่งมอบ")
    else:
        try:
            pdf_data = generate_pdf()
            st.success("สร้าง PDF สำเร็จ!")
            st.download_button(
                label="📥 ดาวน์โหลด PDF",
                data=bytes(pdf_data),
                file_name=f"CPRAM_{s_name}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
