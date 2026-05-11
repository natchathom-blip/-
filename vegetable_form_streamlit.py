import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

# --- 1. โหลดข้อมูลที่อยู่ ---
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

# --- 2. ตั้งค่าหน้าจอและ Header ---
st.set_page_config(page_title="CPRAM Form", layout="wide")

st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; margin-bottom: 20px;">
        <div style="background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 26px;">cpram</div>
        <div style="text-align: right;"><b>FR-QAS-10-000</b><br><small>มีผลใช้งาน: 2026-05-08</small></div>
    </div>
    """, unsafe_allow_html=True)

# --- 3. ส่วนที่ 1 (ล็อกข้อมูล) ---
st.subheader("ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ")
c1, c2 = st.columns(2)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="s_date")
origin_main = st.selectbox("ประเทศแหล่งปลูกหลัก", ["ประเทศไทย", "จีน", "อื่นๆ"], key="origin_main")

# --- 4. ส่วนที่ 2 (ล็อกที่อยู่ไม่ให้หาย) ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

st.subheader("ส่วนที่ 2 — รายการวัตถุดิบ")

for i in range(st.session_state.items_count):
    with st.container():
        st.markdown(f'<div style="background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 15px;">', unsafe_allow_html=True)
        st.write(f"**รายการที่ {i+1}**")
        
        # ข้อมูลวัตถุดิบ
        r1, r2 = st.columns([3, 1])
        r1.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        r2.number_input("จำนวน (KG)", key=f"qty_{i}", min_value=0.0)

        # วันเวลา เก็บเกี่ยว/ล้าง
        c_h1, c_h2, c_c1, c_c2 = st.columns(4)
        c_h1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
        c_h2.text_input("เวลาเก็บเกี่ยว", key=f"ht_{i}")
        c_c1.date_input("วันที่ล้าง", key=f"cd_{i}")
        c_c2.text_input("เวลาล้าง", key=f"ct_{i}")

        # --- จุดแก้ไขสำคัญ: ล็อกที่อยู่ไม่ให้หาย ---
        st.markdown("📍 **ที่อยู่แหล่งปลูก**")
        if origin_main == "ประเทศไทย" and not df_addr.empty:
            a1, a2, a3 = st.columns(3)
            
            # จังหวัด
            prov_list = sorted(df_addr["จังหวัด"].unique().tolist())
            # ใช้ st.selectbox โดยกำหนดค่าเริ่มต้นจาก session_state ถ้ามีอยู่แล้ว
            p_idx = 0
            if f"p_{i}" in st.session_state and st.session_state[f"p_{i}"] in prov_list:
                p_idx = prov_list.index(st.session_state[f"p_{i}"]) + 1
            
            sel_prov = a1.selectbox("จังหวัด", ["- เลือก -"] + prov_list, key=f"p_{i}", index=p_idx)
            
            # อำเภอ
            dist_list = []
            if sel_prov != "- เลือก -":
                dist_list = sorted(df_addr[df_addr["จังหวัด"] == sel_prov]["อำเภอ"].unique().tolist())
            
            d_idx = 0
            if f"a_{i}" in st.session_state and st.session_state[f"a_{i}"] in dist_list:
                d_idx = dist_list.index(st.session_state[f"a_{i}"]) + 1
                
            sel_dist = a2.selectbox("อำเภอ", ["- เลือก -"] + dist_list, key=f"a_{i}", index=d_idx)
            
            # ตำบล
            sub_list = []
            if sel_dist != "- เลือก -":
                sub_list = sorted(df_addr[(df_addr["จังหวัด"] == sel_prov) & (df_addr["อำเภอ"] == sel_dist)]["ตำบล"].unique().tolist())
            
            t_idx = 0
            if f"t_{i}" in st.session_state and st.session_state[f"t_{i}"] in sub_list:
                t_idx = sub_list.index(st.session_state[f"t_{i}"]) + 1
                
            sel_sub = a3.selectbox("ตำบล", ["- เลือก -"] + sub_list, key=f"t_{i}", index=t_idx)
        else:
            a1, a2, a3 = st.columns(3)
            a1.text_input("จังหวัด", key=f"p_man_{i}")
            a2.text_input("อำเภอ", key=f"a_man_{i}")
            a3.text_input("ตำบล", key=f"t_man_{i}")

        st.markdown('</div>', unsafe_allow_html=True)

# ปุ่มเพิ่มรายการ
if st.button("+ เพิ่มรายการวัตถุดิบ"):
    st.session_state.items_count += 1
    st.rerun()

# --- 5. ปุ่มสร้าง PDF (หัวกระดาษตามรูป) ---
st.write("---")
if st.button("✅ ยืนยันข้อมูลและดาวน์โหลด PDF", type="primary", use_container_width=True):
    if not st.session_state.s_name:
        st.error("กรุณากรอกชื่อผู้ส่งมอบ")
    else:
        pdf = FPDF()
        pdf.add_page()
        
        # โหลดฟอนต์ (ต้องมีไฟล์ Sarabun-Regular.ttf ในโฟลเดอร์เดียวกับโค้ด)
        font_path = "Sarabun-Regular.ttf"
        if os.path.exists(font_path):
            pdf.add_font('Sarabun', '', font_path)
            pdf.set_font('Sarabun', '', 14)
        else:
            pdf.set_font('Arial', '', 12)

        # วาด Header เลียนแบบรูปภาพ
        pdf.set_fill_color(46, 125, 50)
        pdf.rect(10, 10, 30, 10, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.text(14, 17, "cpram")
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Sarabun', '', 10)
        pdf.text(160, 14, "FR-QAS-10-000")
        pdf.text(155, 19, "Effective: 2026-05-08")
        pdf.line(10, 22, 200, 22)

        pdf.ln(20)
        pdf.set_font('Sarabun', '', 16)
        pdf.cell(0, 10, "แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบ", ln=True, align='C')
        
        # ดึงข้อมูลจาก Session State มาแสดงทั้งหมด
        pdf.set_font('Sarabun', '', 12)
        pdf.ln(5)
        pdf.cell(0, 8, f"ผู้ส่งมอบ: {st.session_state.s_name}", ln=True)
        pdf.cell(0, 8, f"วันที่ส่ง: {st.session_state.s_date}", ln=True)
        
        for i in range(st.session_state.items_count):
            pdf.ln(3)
            pdf.cell(0, 8, f"รายการที่ {i+1}: {st.session_state.get(f'mat_{i}')} จำนวน {st.session_state.get(f'qty_{i}')} KG", ln=True)
            pdf.cell(0, 8, f"เก็บเกี่ยว: {st.session_state.get(f'hd_{i}')} {st.session_state.get(f'ht_{i}')} | ล้าง: {st.session_state.get(f'cd_{i}')} {st.session_state.get(f'ct_{i}')}", ln=True)
            pdf.cell(0, 8, f"ที่อยู่: จ.{st.session_state.get(f'p_{i}')} อ.{st.session_state.get(f'a_{i}')} ต.{st.session_state.get(f't_{i}')}", ln=True)

        pdf_output = pdf.output()
        st.download_button(
            label="📥 คลิกโหลดไฟล์ PDF",
            data=bytes(pdf_output),
            file_name=f"CPRAM_{st.session_state.s_name}.pdf",
            mime="application/pdf"
        )
