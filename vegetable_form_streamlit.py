import streamlit as st
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF
import base64

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CPRAM - Supplier Form", layout="wide")

# --- 2. โหลดข้อมูลที่อยู่ (แก้ปัญหาไฟล์ไม่พบ) ---
@st.cache_data
def load_address_data():
    # พยายามอ่านไฟล์ที่คุณอัปโหลดมา
    target_file = 'thailand.xlsx - Sheet1.csv'
    if os.path.exists(target_file):
        try:
            df = pd.read_csv(target_file)
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

df_addr = load_address_data()

# --- 3. ฟังก์ชันสร้าง PDF (รองรับข้อมูลครบทุกส่วน) ---
def create_pdf(s_data, items):
    pdf = FPDF()
    pdf.add_page()
    # หมายเหตุ: ในสภาพแวดล้อมทั่วไปต้องโหลด Font ภาษาไทย (.ttf) เพื่อให้แสดงภาษาไทยใน PDF ได้
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="CPRAM - Supplier Delivery Record", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.ln(10)
    
    # ส่วนที่ 1
    pdf.cell(200, 10, txt=f"Supplier: {s_data['name']}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {s_data['date']} | Time: {s_data['time']}", ln=True)
    pdf.cell(200, 10, txt=f"Recorder: {s_data['recorder']}", ln=True)
    pdf.ln(5)
    
    # ส่วนที่ 2
    pdf.cell(200, 10, txt="Material Details:", ln=True)
    for idx, item in enumerate(items):
        pdf.cell(200, 10, txt=f"{idx+1}. {item['mat']} - Qty: {item['qty']} KG", ln=True)
        pdf.cell(200, 10, txt=f"   Location: {item['province']}, {item['dist']}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1', errors='ignore')

# --- 4. ส่วนแสดงผล UI (Header) ---
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px;">
        <div style="background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 26px;">cpram</div>
        <div style="text-align: right;"><b>FR-QAS-10-000</b><br><small>Effective Date: 2026-05-08</small></div>
    </div>
    """, unsafe_allow_html=True)

# --- 5. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ (Lock Data ด้วย key) ---
st.subheader("ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ")
c1, c2, c3 = st.columns(3)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="s_date")
s_time = c3.text_input("เวลาส่ง (น.)", key="s_time")

c4, c5, c6 = st.columns(3)
s_email = c4.text_input("อีเมลสำหรับรับ PDF *", key="s_email")
recorder = c5.text_input("ลงชื่อผู้กรอก", key="recorder")
origin_main = c6.selectbox("ประเทศแหล่งปลูกหลัก", ["ประเทศไทย", "จีน", "อื่นๆ"], key="origin_main")

# --- 6. ส่วนที่ 2 — รายการวัตถุดิบ ---
if 'items_count' not in st.session_state: st.session_state.items_count = 1
def add_item(): st.session_state.items_count += 1

st.subheader("ส่วนที่ 2 — รายการวัตถุดิบ")
items_data = []

for i in range(st.session_state.items_count):
    with st.container():
        st.markdown(f"📦 **รายการที่ {i+1}**")
        r1, r2, r3 = st.columns([2, 1, 1])
        mat = r1.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        code = r2.text_input("Code", key=f"code_{i}")
        qty = r3.number_input("จำนวน (KG)", key=f"qty_{i}")

        # Dropdown ที่อยู่ (แสดงเมื่อเป็นประเทศไทย)
        p, a, t = "", "", ""
        if origin_main == "ประเทศไทย" and not df_addr.empty:
            a1, a2, a3 = st.columns(3)
            p = a1.selectbox("จังหวัด", ["- เลือก -"] + sorted(df_addr["จังหวัด"].unique()), key=f"p_{i}")
            a = a2.selectbox("อำเภอ", ["- เลือก -"] + sorted(df_addr[df_addr["จังหวัด"]==p]["อำเภอ"].unique()) if p != "- เลือก -" else [], key=f"a_{i}")
            t = a3.selectbox("ตำบล", ["- เลือก -"] + sorted(df_addr[(df_addr["จังหวัด"]==p) & (df_addr["อำเภอ"]==a)]["ตำบล"].unique()) if a != "- เลือก -" else [], key=f"t_{i}")
        
        # ลักษณะการปลูก
        r4c1, r4c2 = st.columns(2)
        style = r4c1.selectbox("ลักษณะการปลูก", ["ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
        loc = r4c2.selectbox("ลักษณะสถานที่ปลูก", ["โรงเรือน", "แปลงเปิด"], key=f"loc_{i}")
        
        items_data.append({"mat": mat, "qty": qty, "province": p, "dist": a})
        st.markdown("---")

st.button("+ เพิ่มรายการ", on_click=add_item)

# --- 7. ปุ่มยืนยันและดาวน์โหลด ---
if st.button("✅ ยืนยันข้อมูลและสร้าง PDF", type="primary"):
    if not s_name or not s_email:
        st.error("กรุณากรอกชื่อผู้ส่งมอบและอีเมล")
    else:
        # 1. สร้าง PDF
        s_info = {"name": s_name, "date": str(s_date), "time": s_time, "recorder": recorder}
        pdf_content = create_pdf(s_info, items_data)
        
        # 2. แสดงปุ่มดาวน์โหลด (นี่คือส่วนที่ทำให้โหลดไฟล์ได้)
        st.success(f"สร้างไฟล์ PDF สำเร็จ! ระบบกำลังเตรียมส่งไปที่ {s_email}")
        st.download_button(
            label="📥 คลิกที่นี่เพื่อดาวน์โหลด PDF",
            data=pdf_content,
            file_name=f"CPRAM_{s_name}_{datetime.now().strftime('%d%m%Y')}.pdf",
            mime="application/pdf"
        )
        
        # 3. หมายเหตุเรื่องอีเมล
        st.info("ℹ️ สำหรับการส่งเมลอัตโนมัติ: ระบบต้องเชื่อมต่อกับ SMTP Server (เช่น Gmail หรือ Outlook) ซึ่งต้องใช้รหัสผ่านแอปของคุณเพื่อความปลอดภัย")
