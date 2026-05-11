import streamlit as st
import pandas as pd
import os
from fpdf import FPDF

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CPRAM Supplier Form", layout="wide")

# --- 2. ฟังก์ชันโหลดข้อมูลที่อยู่ (แก้ไขชื่อไฟล์ให้ตรงกับ GitHub) ---
@st.cache_data
def load_address_data():
    # แก้เป็นชื่อไฟล์จริงใน GitHub ของคุณ
    file_path = 'thailand.xlsx' 
    if os.path.exists(file_path):
        try:
            # อ่านไฟล์ .xlsx
            df = pd.read_excel(file_path)
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"Error: {e}")
            return pd.DataFrame()
    else:
        st.error(f"❌ ไม่พบไฟล์ {file_path} ในระบบ")
        return pd.DataFrame()

df_addr = load_address_data()

# --- 3. ส่วนหัว Header ---
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; margin-bottom: 20px;">
        <div style="background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 26px;">cpram</div>
        <div style="text-align: right;"><b>FR-QAS-10-000</b><br><small>มีผลใช้งาน: 2026-05-08</small></div>
    </div>
    """, unsafe_allow_html=True)

# --- 4. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ ---
st.subheader("ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ")
c1, c2 = st.columns(2)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
origin_main = c2.selectbox("ประเทศแหล่งปลูกหลัก", ["ประเทศไทย", "จีน", "อื่นๆ"], key="origin_main")

# --- 5. ส่วนที่ 2 — รายการวัตถุดิบ (ล็อกข้อมูลที่อยู่) ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

for i in range(st.session_state.items_count):
    with st.container():
        st.markdown(f'<div style="background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 15px;">', unsafe_allow_html=True)
        st.write(f"**รายการที่ {i+1}**")
        
        r1, r2 = st.columns([3, 1])
        r1.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        r2.number_input("จำนวน (KG)", key=f"qty_{i}", min_value=0.0)

        # Dropdown ที่อยู่ (ดึงจากไฟล์ thailand.xlsx)
        st.markdown("📍 **ที่อยู่แหล่งปลูก**")
        if origin_main == "ประเทศไทย" and not df_addr.empty:
            a1, a2, a3 = st.columns(3)
            
            # จังหวัด
            p_list = sorted(df_addr["จังหวัด"].unique().tolist())
            p_val = a1.selectbox("จังหวัด", ["- เลือก -"] + p_list, key=f"p_{i}")
            
            # อำเภอ
            d_list = sorted(df_addr[df_addr["จังหวัด"] == p_val]["อำเภอ"].unique().tolist()) if p_val != "- เลือก -" else []
            a_val = a2.selectbox("อำเภอ", ["- เลือก -"] + d_list, key=f"a_{i}")
            
            # ตำบล
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

# --- 6. ปุ่มสร้าง PDF (แก้ไข Error ภาษาไทย) ---
st.write("---")
if st.button("✅ ยืนยันข้อมูลและรับ PDF", type="primary", use_container_width=True):
    if not s_name:
        st.error("กรุณากรอกชื่อผู้ส่งมอบ")
    else:
        pdf = FPDF()
        pdf.add_page()
        
        # ล็อกการโหลดฟอนต์ให้ตรงกับชื่อไฟล์ใน GitHub
        font_file = "Sarabun-Regular.ttf"
        if os.path.exists(font_file):
            pdf.add_font('Sarabun', '', font_file, uni=True)
            pdf.set_font('Sarabun', '', 16)
            
            # เขียนข้อมูลลง PDF
            pdf.cell(0, 10, txt=f"ผู้ส่งมอบ: {s_name}", ln=True)
            for i in range(st.session_state.items_count):
                pdf.cell(0, 10, txt=f"รายการที่ {i+1}: {st.session_state.get(f'mat_{i}')}", ln=True)
            
            # ส่งไฟล์ให้ดาวน์โหลด
            pdf_out = pdf.output(dest='S').encode('latin-1', 'replace')
            st.download_button("📥 ดาวน์โหลดไฟล์ PDF ที่นี่", data=pdf_out, file_name="CPRAM_Form.pdf", mime="application/pdf")
        else:
            st.error(f"❌ ไม่พบไฟล์ฟอนต์ {font_file} กรุณาตรวจสอบใน GitHub")
