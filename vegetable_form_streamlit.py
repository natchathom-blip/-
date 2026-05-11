import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

# --- 1. ตั้งค่าหน้าจอและดึงข้อมูลที่อยู่ ---
st.set_page_config(page_title="CPRAM Supplier Form", layout="wide")

@st.cache_data
def load_address_data():
    # ดึงข้อมูลจากไฟล์ thailand.xlsx ใน GitHub 
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

# --- 2. ส่วนหัว Header (ตามรูปแบบ FR-QAS-10-000) ---
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; margin-bottom: 20px;">
        <div style="background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 26px;">cpram</div>
        <div style="text-align: right;"><b>FR-QAS-10-000</b><br><small>มีผลใช้งาน: 2026-05-08</small></div>
    </div>
    """, unsafe_allow_html=True)

st.subheader("แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด") [cite: 1]

# --- 3. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ (Lock ข้อมูลด้วย key) ---
st.markdown("#### ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ")
c1, c2, c3 = st.columns(3)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name") [cite: 2]
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="s_date") [cite: 4]
s_time = c3.text_input("เวลาส่ง (น.)", key="s_time", placeholder="เช่น 14:00")

c4, c5, c6 = st.columns(3)
s_email = c4.text_input("อีเมลสำหรับรับ PDF *", key="s_email")
recorder = c5.text_input("ลงชื่อผู้กรอก", key="recorder") [cite: 27]
origin_main = c6.selectbox("ประเทศแหล่งปลูกหลัก *", ["ประเทศไทย", "จีน", "อื่นๆ"], key="origin_main")

# --- 4. ส่วนที่ 2 — รายการวัตถุดิบ (ข้อมูลครบตามใบนำส่ง) ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

st.markdown("#### ส่วนที่ 2 — รายการวัตถุดิบ")

for i in range(st.session_state.items_count):
    with st.container():
        st.markdown(f'<div style="background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 15px;">', unsafe_allow_html=True)
        
        # ส่วนหัวและปุ่มลบ
        col_h, col_del = st.columns([0.9, 0.1])
        col_h.markdown(f"**รายการที่ {i+1}**")
        if st.session_state.items_count > 1 and col_del.button(f"✕", key=f"del_{i}"):
            st.session_state.items_count -= 1
            st.rerun()

        # แถวที่ 1: ข้อมูลพื้นฐาน [cite: 6, 8, 9]
        r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
        r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}") [cite: 6]
        r1c2.text_input("Code", key=f"code_{i}") [cite: 8]
        r1c3.number_input("จำนวน (KG) *", min_value=0.0, key=f"qty_{i}") [cite: 9]

        # แถวที่ 2: รายละเอียดการปลูก [cite: 10, 11, 12]
        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.text_input("สายพันธุ์", key=f"breed_{i}") [cite: 10]
        r2c2.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}") [cite: 11]
        r2c3.selectbox("ระบบการปลูก", ["- เลือก -", "โรงเรือน/ระบบปิด", "แปลงเปิด/ระบบเปิด"], key=f"sys_{i}") [cite: 12]

        # แถวที่ 3: วันเวลาเก็บเกี่ยวและล้าง [cite: 13, 15, 17, 19]
        r3c1, r3c2, r3c3, r3c4 = st.columns(4)
        r3c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}") [cite: 13]
        r3c2.text_input("เวลาเก็บเกี่ยว", key=f"ht_{i}", placeholder="04:00") [cite: 15]
        r3c3.date_input("วันที่ล้าง/ตัดแต่ง", key=f"cd_{i}") [cite: 17]
        r3c4.text_input("เวลาล้าง/ตัดแต่ง", key=f"ct_{i}", placeholder="06:00") [cite: 19]

        # แถวที่ 4: ข้อมูลฟาร์ม [cite: 21, 23, 25]
        r4c1, r4c2, r4c3 = st.columns(3)
        r4c1.text_input("ชื่อผู้ปลูก", key=f"grower_{i}") [cite: 21]
        r4c2.text_input("เลขที่ GAP", key=f"gap_{i}") [cite: 23]
        r4c3.text_input("รหัสไร่", key=f"farm_{i}") [cite: 25]

        # ส่วนที่อยู่ (Dropdown ล็อกข้อมูลไม่ให้หาย) 
        st.markdown("📍 **ที่อยู่แหล่งปลูก**")
        if origin_main == "ประเทศไทย" and not df_addr.empty:
            a1, a2, a3 = st.columns(3)
            
            # จังหวัด
            p_opts = ["- เลือก -"] + sorted(df_addr["จังหวัด"].unique().tolist())
            p_idx = p_opts.index(st.session_state[f"p_{i}"]) if f"p_{i}" in st.session_state and st.session_state[f"p_{i}"] in p_opts else 0
            sel_p = a1.selectbox("จังหวัด", p_opts, key=f"p_{i}", index=p_idx)
            
            # อำเภอ
            d_opts = ["- เลือก -"] + sorted(df_addr[df_addr["จังหวัด"] == sel_p]["อำเภอ"].unique().tolist()) if sel_p != "- เลือก -" else ["- เลือก -"]
            d_idx = d_opts.index(st.session_state[f"a_{i}"]) if f"a_{i}" in st.session_state and st.session_state[f"a_{i}"] in d_opts else 0
            sel_d = a2.selectbox("อำเภอ", d_opts, key=f"a_{i}", index=d_idx)
            
            # ตำบล
            t_opts = ["- เลือก -"] + sorted(df_addr[(df_addr["จังหวัด"] == sel_p) & (df_addr["อำเภอ"] == sel_d)]["ตำบล"].unique().tolist()) if sel_d != "- เลือก -" else ["- เลือก -"]
            t_idx = t_opts.index(st.session_state[f"t_{i}"]) if f"t_{i}" in st.session_state and st.session_state[f"t_{i}"] in t_opts else 0
            sel_t = a3.selectbox("ตำบล", t_opts, key=f"t_{i}", index=t_idx)
        else:
            a1, a2, a3 = st.columns(3)
            a1.text_input("จังหวัด/มณฑล", key=f"p_man_{i}")
            a2.text_input("อำเภอ/เมือง", key=f"a_man_{i}")
            a3.text_input("ตำบล/แขวง", key=f"t_man_{i}")

        st.markdown('</div>', unsafe_allow_html=True)

if st.button("+ เพิ่มรายการวัตถุดิบ"):
    st.session_state.items_count += 1
    st.rerun()

# --- 5. ปุ่มสร้าง PDF (ใช้ฟอนต์ Sarabun-Regular.ttf) ---
st.write("---")
if st.button("✅ ยืนยันข้อมูลและดาวน์โหลด PDF", type="primary", use_container_width=True):
    if not st.session_state.s_name:
        st.error("กรุณากรอกชื่อผู้ส่งมอบ")
    else:
        pdf = FPDF()
        pdf.add_page()
        
        font_path = "Sarabun-Regular.ttf"
        if os.path.exists(font_path):
            pdf.add_font('Sarabun', '', font_path, uni=True)
            pdf.set_font('Sarabun', '', 14)
            
            # ส่วนหัวเอกสาร
            pdf.cell(0, 10, f"ผู้ส่งมอบ: {st.session_state.s_name}", ln=True)
            pdf.cell(0, 10, f"วันที่ส่ง: {st.session_state.s_date}", ln=True)
            
            for i in range(st.session_state.items_count):
                pdf.ln(5)
                pdf.cell(0, 10, f"รายการที่ {i+1}: {st.session_state.get(f'mat_{i}')} | {st.session_state.get(f'qty_{i}')} KG", ln=True)
            
            # การ encode ป้องกัน Error Character 'บ'
            pdf_out = pdf.output(dest='S').encode('latin-1', 'replace')
            st.download_button("📥 คลิกเพื่อโหลด PDF", data=pdf_out, file_name=f"CPRAM_{st.session_state.s_name}.pdf")
        else:
            st.error("ไม่พบไฟล์ฟอนต์ Sarabun-Regular.ttf ในระบบ")
