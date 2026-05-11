import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

# --- 1. การตั้งค่าหน้าจอและสไตล์ ---
st.set_page_config(page_title="CPRAM Form - Salad Group", layout="wide")

# --- 2. โหลดข้อมูลที่อยู่ ---
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

# --- 3. ส่วนหัวโปรแกรม (UI บน Streamlit) ---
st.markdown("""
    <style>
    .header-container { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; margin-bottom: 20px; }
    .logo-box { background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 26px; }
    </style>
    <div class="header-container">
        <div style="display: flex; align-items: center;">
            <div class="logo-box">cpram</div>
        </div>
        <div style="text-align: right; font-family: sans-serif;">
            <b>FR-QAS-10-000</b><br><small>มีผลใช้งาน: 2026-05-08</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 4. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ (Lock ข้อมูล) ---
st.subheader("แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด")
c1, c2 = st.columns(2)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="s_date")

origin_main = st.selectbox("ประเทศแหล่งปลูกหลัก", ["ประเทศไทย", "จีน", "อื่นๆ"], key="origin_main")

# --- 5. ส่วนที่ 2 — รายการวัตถุดิบ (ข้อมูลไม่หาย) ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

def add_item():
    st.session_state.items_count += 1

for i in range(st.session_state.items_count):
    with st.container():
        st.markdown(f'<div style="background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 15px;">', unsafe_allow_html=True)
        st.markdown(f"**รายการที่ {i+1}**")
        
        # ข้อมูลทั่วไปวัตถุดิบ
        r1, r2, r3 = st.columns([2, 1, 1])
        mat = r1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
        code = r2.text_input("Code", key=f"code_{i}")
        qty = r3.number_input("จำนวน (KG)", key=f"qty_{i}", min_value=0.0)

        # รายละเอียดสายพันธุ์/ระบบการปลูก
        r2c1, r2c2, r2c3 = st.columns(3)
        breed = r2c1.text_input("สายพันธุ์", key=f"breed_{i}")
        style = r2c2.selectbox("ลักษณะการปลูก", ["ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
        system = r2c3.selectbox("ระบบการปลูก", ["ระบบเปิด", "ระบบปิด"], key=f"sys_{i}")

        # วันเวลา เก็บเกี่ยว/ล้าง
        r3c1, r3c2, r3c3, r3c4 = st.columns(4)
        h_date = r3c1.date_input("วันที่เก็บเกี่ยววัตถุดิบ", key=f"hd_{i}")
        h_time = r3c2.text_input("เวลาเก็บเกี่ยว", key=f"ht_{i}", placeholder="03:00")
        c_date = r3c3.date_input("วันที่ล้าง/ตัดแต่ง", key=f"cd_{i}")
        c_time = r3c4.text_input("เวลาล้าง/ตัดแต่ง", key=f"ct_{i}", placeholder="05:00")

        # ข้อมูลผู้ปลูก
        r4c1, r4c2, r4c3 = st.columns(3)
        grower = r4c1.text_input("ชื่อผู้ปลูก", key=f"grow_{i}")
        gap = r4c2.text_input("เลขที่ GAP", key=f"gap_{i}")
        farm_id = r4c3.text_input("รหัสไร่", key=f"farm_{i}")

        # ที่อยู่แหล่งปลูก
        st.markdown("📍 **ที่อยู่แหล่งปลูก**")
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

        st.markdown('</div>', unsafe_allow_html=True)

st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item)

# --- 6. ฟังก์ชันสร้าง PDF (วาดหัวตามรูปแนบ) ---
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # ดึงฟอนต์ Sarabun
    font_path = "Sarabun-Regular.ttf"
    pdf.add_font('Sarabun', '', font_path)
    pdf.set_font('Sarabun', '', 12)

    # --- วาดหัวกระดาษ (Header) ---
    # 1. วาดกล่องเขียวโลโก้
    pdf.set_fill_color(46, 125, 50) # สีเขียว CPRAM
    pdf.rect(15, 10, 35, 12, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Sarabun', '', 18)
    pdf.text(21, 19, "cpram")

    # 2. ข้อความฝั่งขวา
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Sarabun', '', 10)
    pdf.text(165, 15, "FR-QAS-10-000")
    pdf.text(160, 20, "มีผลใช้งาน: 2026-05-08")

    # 3. เส้นขีดคั่นหัวกระดาษ
    pdf.set_draw_color(46, 125, 50)
    pdf.set_line_width(0.5)
    pdf.line(15, 25, 195, 25)

    # --- เนื้อหาแบบฟอร์ม ---
    pdf.set_font('Sarabun', '', 16)
    pdf.ln(20)
    pdf.cell(0, 10, txt="แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด", ln=True, align='C')
    pdf.ln(5)

    pdf.set_font('Sarabun', '', 12)
    pdf.cell(0, 8, txt=f"ผู้ส่งมอบ (Supplier): {st.session_state.s_name}", ln=True)
    pdf.cell(0, 8, txt=f"วันที่ส่งวัตถุดิบ: {st.session_state.s_date}", ln=True)
    pdf.ln(5)

    for i in range(st.session_state.items_count):
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 8, txt=f"{i+1}. รายละเอียดวัตถุดิบ", ln=True, fill=True)
        pdf.cell(0, 8, txt=f"ชนิดวัตถุดิบ: {st.session_state.get(f'mat_{i}')}  Code: {st.session_state.get(f'code_{i}')}  จำนวน: {st.session_state.get(f'qty_{i}')} KG", ln=True)
        pdf.cell(0, 8, txt=f"สายพันธุ์: {st.session_state.get(f'breed_{i}')}  ลักษณะการปลูก: {st.session_state.get(f'style_{i}')}  ระบบ: {st.session_state.get(f'sys_{i}')}", ln=True)
        pdf.cell(0, 8, txt=f"วันที่เก็บเกี่ยว: {st.session_state.get(f'hd_{i}')} เวลา: {st.session_state.get(f'ht_{i}')}", ln=True)
        pdf.cell(0, 8, txt=f"วันที่ล้าง/ตัดแต่ง: {st.session_state.get(f'cd_{i}')} เวลา: {st.session_state.get(f'ct_{i}')}", ln=True)
        pdf.cell(0, 8, txt=f"ชื่อผู้ปลูก: {st.session_state.get(f'grow_{i}')}  เลขที่ GAP: {st.session_state.get(f'gap_{i}')}  รหัสไร่: {st.session_state.get(f'farm_{i}')}", ln=True)
        
        # ที่อยู่
        p = st.session_state.get(f'p_{i}', '')
        a = st.session_state.get(f'a_{i}', '')
        t = st.session_state.get(f't_{i}', '')
        pdf.cell(0, 8, txt=f"ที่อยู่แหล่งปลูก: จ.{p} อ.{a} ต.{t}", ln=True)
        pdf.ln(5)

    # ส่วนท้าย (Signature)
    pdf.ln(10)
    pdf.cell(90, 8, txt="ลงชื่อ..........................................................", ln=False)
    pdf.cell(90, 8, txt="วันที่..........................................................", ln=True)

    return pdf.output()

# --- 7. ปุ่มดำเนินการ ---
st.write("---")
if st.button("✅ ยืนยันและดาวน์โหลด PDF", type="primary", use_container_width=True):
    if not s_name:
        st.error("กรุณากรอกชื่อผู้ส่งมอบ")
    else:
        pdf_data = generate_pdf()
        st.download_button(
            label="📥 คลิกเพื่อโหลดไฟล์ PDF",
            data=bytes(pdf_data),
            file_name=f"Salad_Survey_{s_name}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
