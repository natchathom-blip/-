import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CPRAM Supplier Form", layout="wide")

# --- 2. ฟังก์ชันโหลดข้อมูลที่อยู่ (Dropdown) ---
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

# --- 3. ส่วนหัวกระดาษ (Header) ตามรูปภาพ ---
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; margin-bottom: 20px;">
        <div style="background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 26px;">cpram</div>
        <div style="text-align: right;"><b>FR-QAS-10-000</b><br><small>มีผลใช้งาน: 2026-05-08</small></div>
    </div>
    """, unsafe_allow_html=True)

st.subheader("แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด")

# --- 4. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ (Lock ข้อมูลด้วย key) ---
st.markdown("#### ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ")
c1, c2, c3 = st.columns(3)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="s_date")
s_time = c3.text_input("เวลาส่ง (น.)", key="s_time")

c4, c5, c6 = st.columns(3)
s_email = c4.text_input("อีเมลสำหรับรับ PDF *", key="s_email")
recorder = c5.text_input("ลงชื่อผู้กรอก", key="recorder")
origin_main = c6.selectbox("ประเทศแหล่งปลูกหลัก *", ["ประเทศไทย", "จีน", "อื่นๆ"], key="origin_main")

# --- 5. ส่วนที่ 2 — รายการวัตถุดิบ (ล็อกข้อมูลรายรายการ) ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

def add_item():
    st.session_state.items_count += 1

st.markdown("#### ส่วนที่ 2 — รายการวัตถุดิบ")

for i in range(st.session_state.items_count):
    with st.container():
        st.markdown(f'<div style="background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 15px;">', unsafe_allow_html=True)
        
        col_h, col_del = st.columns([0.9, 0.1])
        col_h.markdown(f"**รายการที่ {i+1}**")
        if st.session_state.items_count > 1 and col_del.button(f"✕", key=f"del_{i}"):
            st.session_state.items_count -= 1
            st.rerun()

        # แถวข้อมูลวัตถุดิบ
        r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
        r1c1.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        r1c2.text_input("Code", key=f"code_{i}")
        r1c3.number_input("จำนวน (KG)", min_value=0.0, key=f"qty_{i}")

        # วันเวลา เก็บเกี่ยว/ล้าง
        r3c1, r3c2, r3c3, r3c4 = st.columns(4)
        r3c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
        r3c2.text_input("เวลาเก็บเกี่ยว", key=f"ht_{i}", placeholder="04:00")
        r3c3.date_input("วันที่ล้าง/ตัดแต่ง", key=f"cd_{i}")
        r3c4.text_input("เวลาล้าง/ตัดแต่ง", key=f"ct_{i}", placeholder="06:00")

        # ที่อยู่แหล่งปลูก (Dropdown)
        st.markdown("📍 **ที่อยู่แหล่งปลูก**")
        if origin_main == "ประเทศไทย" and not df_addr.empty:
            a1, a2, a3 = st.columns(3)
            p_list = sorted(df_addr["จังหวัด"].unique().tolist())
            p_val = a1.selectbox("จังหวัด", ["- เลือก -"] + p_list, key=f"p_{i}")
            
            dist_opts = sorted(df_addr[df_addr["จังหวัด"] == p_val]["อำเภอ"].unique().tolist()) if p_val != "- เลือก -" else []
            a_val = a2.selectbox("อำเภอ", ["- เลือก -"] + dist_opts, key=f"a_{i}")
            
            sub_opts = sorted(df_addr[(df_addr["จังหวัด"] == p_val) & (df_addr["อำเภอ"] == a_val)]["ตำบล"].unique().tolist()) if a_val != "- เลือก -" else []
            t_val = a3.selectbox("ตำบล", ["- เลือก -"] + sub_opts, key=f"t_{i}")
        else:
            a1, a2, a3 = st.columns(3)
            a1.text_input("จังหวัด", key=f"p_man_{i}")
            a2.text_input("อำเภอ", key=f"a_man_{i}")
            a3.text_input("ตำบล", key=f"t_man_{i}")

        st.markdown('</div>', unsafe_allow_html=True)

st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item)

# --- 6. ฟังก์ชันสร้าง PDF (แก้ไขวงเล็บและภาษาไทย) ---
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # ใช้ฟอนต์ที่คุณแจ้งชื่อมา
    font_path = "Sarabun-Regular.ttf"
    if os.path.exists(font_path):
        pdf.add_font('Sarabun', '', font_path)
        pdf.set_font('Sarabun', '', 14)
    else:
        pdf.set_font('Arial', '', 12)

    # วาด Header ใน PDF
    pdf.set_fill_color(46, 125, 50)
    pdf.rect(10, 10, 30, 10, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.text(14, 17, "cpram")
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Sarabun', '', 10)
    pdf.text(160, 14, "FR-QAS-10-000")
    pdf.text(155, 19, "Effective: 2026-05-08")
    pdf.line(10, 22, 200, 22)

    # เนื้อหา PDF
    pdf.ln(20)
    pdf.set_font('Sarabun', '', 16)
    pdf.cell(0, 10, "แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบ", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font('Sarabun', '', 12)
    pdf.cell(0, 8, f"ผู้ส่งมอบ: {st.session_state.s_name}", ln=True)
    pdf.cell(0, 8, f"วันที่: {st.session_state.s_date}", ln=True)
    
    for i in range(st.session_state.items_count):
        pdf.ln(5)
        mat = st.session_state.get(f'mat_{i}', '-')
        qty = st.session_state.get(f'qty_{i}', 0)
        pdf.cell(0, 8, f"รายการที่ {i+1}: {mat} | จำนวน: {qty} KG", ln=True)
        
    return pdf.output()

# --- 7. ปุ่มดำเนินการ ---
st.write("---")
if st.button("✅ ยืนยันข้อมูลและดาวน์โหลด PDF", type="primary", use_container_width=True):
    if not st.session_state.s_name:
        st.error("กรุณากรอกชื่อผู้ส่งมอบ")
    else:
        try:
            pdf_data = generate_pdf()
            st.download_button(
                label="📥 คลิกเพื่อโหลด PDF",
                data=bytes(pdf_data),
                file_name=f"CPRAM_{st.session_state.s_name}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
