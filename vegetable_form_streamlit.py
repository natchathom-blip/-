import streamlit as st
import pandas as pd
import os
import base64
from fpdf import FPDF
from datetime import datetime

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CPRAM Supplier Form", layout="wide")

# ฟังก์ชันแปลงรูปภาพเป็น Base64 เพื่อป้องกันปัญหา [Logo Missing]
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# โหลดข้อมูลที่อยู่จากไฟล์ใน GitHub
@st.cache_data
def load_address_data():
    file_path = 'thailand.xlsx' 
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path)
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

df_addr = load_address_data()

# --- 2. ส่วนหัวกระดาษ (Header) ---
logo_path = "image_9482bc.png" # ใช้ไฟล์ภาพโลโก้ตามรูปแนบ
logo_base64 = get_image_base64(logo_path)

header_html = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #2e7d32; padding-bottom: 10px; margin-bottom: 20px;">
        <div>
            {f'<img src="data:image/png;base64,{logo_base64}" width="180">' if logo_base64 else '<b style="color:red;">[Logo Missing]</b>'}
        </div>
        <div style="text-align: right; line-height: 1.2;">
            <b style="font-size: 20px; color: #333;">FR-QAS-10-000</b><br>
            <span style="font-size: 14px; color: #666;">มีผลใช้งาน: 2026-05-08</span>
        </div>
    </div>
"""
st.markdown(header_html, unsafe_allow_html=True)
st.subheader("แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด") # [cite: 1]

# --- 3. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ ---
st.markdown("#### ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ")
c1, c2, c3 = st.columns(3)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name") # [cite: 2]
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="s_date") # [cite: 4]
origin_main = c3.selectbox("ประเทศแหล่งปลูกหลัก *", ["ประเทศไทย", "จีน", "อื่นๆ"], key="origin_main")

# --- 4. ส่วนที่ 2 — รายการวัตถุดิบ (ข้อมูลครบถ้วนตาม PDF) [cite: 6-25] ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

for i in range(st.session_state.items_count):
    with st.container():
        st.markdown(f'<div style="background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 15px;">', unsafe_allow_html=True)
        st.write(f"**รายการที่ {i+1}**")
        
        # แถวที่ 1: ชนิด Code จำนวน [cite: 6, 8, 9]
        r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
        r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
        r1c2.text_input("Code", key=f"code_{i}")
        r1c3.number_input("จำนวน (KG) *", min_value=0.0, key=f"qty_{i}")

        # แถวที่ 2: สายพันธุ์ และการปลูก [cite: 10, 11, 12]
        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.text_input("สายพันธุ์", key=f"breed_{i}")
        r2c2.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
        r2c3.selectbox("ระบบการปลูก", ["- เลือก -", "โรงเรือน/ระบบปิด", "แปลงเปิด/ระบบเปิด"], key=f"sys_{i}")

        # แถวที่ 3: วันที่และเวลาเก็บเกี่ยว/ล้าง [cite: 13, 15, 17, 19]
        r3c1, r3c2, r3c3, r3c4 = st.columns(4)
        r3c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
        r3c2.text_input("เวลาเก็บเกี่ยว", key=f"ht_{i}", placeholder="04:00")
        r3c3.date_input("วันที่ล้าง/ตัดแต่ง", key=f"cd_{i}")
        r3c4.text_input("เวลาล้าง/ตัดแต่ง", key=f"ct_{i}", placeholder="06:00")

        # แถวที่ 4: ข้อมูลฟาร์ม [cite: 21, 23, 25]
        r4c1, r4c2, r4c3 = st.columns(3)
        r4c1.text_input("ชื่อผู้ปลูก", key=f"grower_{i}")
        r4c2.text_input("เลขที่ GAP", key=f"gap_{i}")
        r4c3.text_input("รหัสไร่", key=f"farm_{i}")

        # ที่อยู่แหล่งปลูก
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

if st.button("+ เพิ่มรายการวัตถุดิบ"):
    st.session_state.items_count += 1
    st.rerun()

# --- 5. การสร้าง PDF (แก้ไขปัญหา Character "บ" และการโหลดฟอนต์) ---
st.write("---")
if st.button("✅ ยืนยันข้อมูลและดาวน์โหลด PDF", type="primary", use_container_width=True):
    if not s_name:
        st.error("กรุณากรอกชื่อผู้ส่งมอบ")
    else:
        pdf = FPDF()
        pdf.add_page()
        # ใช้ Sarabun-Regular.ttf เพื่อรองรับภาษาไทย
        font_path = "Sarabun-Regular.ttf"
        if os.path.exists(font_path):
            pdf.add_font('Sarabun', '', font_path, uni=True)
            pdf.set_font('Sarabun', '', 16)
            
            # หัวข้อ PDF
            pdf.cell(0, 10, f"แบบบันทึกข้อมูลผู้ส่งมอบ: {s_name}", ln=True, align='C')
            pdf.set_font('Sarabun', '', 12)
            pdf.cell(0, 10, f"วันที่ส่ง: {s_date}", ln=True)
            
            for i in range(st.session_state.items_count):
                pdf.ln(5)
                pdf.cell(0, 8, f"รายการ {i+1}: {st.session_state.get(f'mat_{i}')} | Code: {st.session_state.get(f'code_{i}')}", ln=True)
                pdf.cell(0, 8, f"ที่อยู่: {st.session_state.get(f'p_{i}')} {st.session_state.get(f'a_{i}')} {st.session_state.get(f't_{i}')}", ln=True)
            
            # ใช้ latin-1 replace เพื่อป้องกัน Error ตอนดาวน์โหลด
            pdf_data = pdf.output(dest='S').encode('latin-1', 'replace')
            st.download_button("📥 คลิกที่นี่เพื่อบันทึกไฟล์ PDF", data=pdf_data, file_name=f"CPRAM_Form_{s_name}.pdf")
        else:
            st.error("ไม่พบไฟล์ฟอนต์ Sarabun-Regular.ttf ใน GitHub")
