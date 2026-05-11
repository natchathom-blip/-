import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

# --- 1. ตั้งค่าหน้าจอและดึงข้อมูลที่อยู่ ---
st.set_page_config(page_title="CPRAM Supplier Form", layout="wide")

@st.cache_data
def load_address_data():
    file_path = 'thailand.xlsx' #
    if os.path.exists(file_path):
        try:
            # อ่านจากไฟล์ Excel โดยตรง
            df = pd.read_excel(file_path)
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

df_addr = load_address_data()

# --- 2. เปลี่ยนหัวกระดาษใหม่ (ตามภาพ image_948a1f.png และ image_9489c3.png) ---
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2px solid #2e7d32; padding-bottom: 10px; margin-bottom: 25px;">
        <img src="https://www.cpram.co.th/images/logo.png" width="120"> <div style="text-align: right; line-height: 1.2;">
            <b style="font-size: 18px; color: #333;">FR-QAS-10-000</b><br>
            <span style="font-size: 14px; color: #666;">มีผลใช้งาน: 2026-05-08</span>
        </div>
    </div>
    """, unsafe_allow_html=True) #

st.subheader("แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด")

# --- 3. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ (ลบช่อง Email และ ผู้ลงชื่อออก) ---
st.markdown("#### ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ")
c1, c2, c3 = st.columns(3)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="s_date")
origin_main = c3.selectbox("ประเทศแหล่งปลูกหลัก *", ["ประเทศไทย", "จีน", "อื่นๆ"], key="origin_main")

# --- 4. ส่วนที่ 2 — รายการวัตถุดิบ (ข้อมูลครบตามใบนำส่ง) ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

for i in range(st.session_state.items_count):
    with st.container():
        st.markdown(f'<div style="background-color: #f9fdf9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 15px;">', unsafe_allow_html=True)
        
        col_h, col_del = st.columns([0.9, 0.1])
        col_h.markdown(f"**รายการที่ {i+1}**")
        if st.session_state.items_count > 1 and col_del.button(f"✕", key=f"del_{i}"):
            st.session_state.items_count -= 1
            st.rerun()

        # แถวข้อมูลสินค้า [cite: 6-12]
        r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
        r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
        r1c2.text_input("Code", key=f"code_{i}")
        r1c3.number_input("จำนวน (KG) *", min_value=0.0, key=f"qty_{i}")

        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.text_input("สายพันธุ์", key=f"breed_{i}")
        r2c2.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
        r2c3.selectbox("ระบบการปลูก", ["- เลือก -", "โรงเรือน/ระบบปิด", "แปลงเปิด/ระบบเปิด"], key=f"sys_{i}")

        # แถววันเวลา [cite: 13-20]
        r3c1, r3c2, r3c3, r3c4 = st.columns(4)
        r3c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
        r3c2.time_input("เวลาเก็บเกี่ยว", key=f"ht_{i}")
        r3c3.date_input("วันที่ล้าง/ตัดแต่ง", key=f"cd_{i}")
        r3c4.time_input("เวลาล้าง/ตัดแต่ง", key=f"ct_{i}")

        # แถวข้อมูลฟาร์ม [cite: 21-25]
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

# --- 5. ฟังก์ชันสร้าง PDF (แก้ไข Unicode และหัวกระดาษ) ---
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # ดึงฟอนต์ Sarabun-Regular.ttf ที่มีอยู่ใน GitHub
    font_path = "Sarabun-Regular.ttf"
    if os.path.exists(font_path):
        pdf.add_font('Sarabun', '', font_path, uni=True)
        pdf.set_font('Sarabun', '', 14)
    else:
        # Fallback กรณีหาฟอนต์ไม่เจอ จะแจ้งเตือนแทนการปล่อยให้ Crash
        return None

    # วาดหัวกระดาษใน PDF
    pdf.set_font('Sarabun', '', 10)
    pdf.cell(0, 5, "FR-QAS-10-000", ln=True, align='R')
    pdf.cell(0, 5, "มีผลใช้งาน: 2026-05-08", ln=True, align='R')
    pdf.line(10, 22, 200, 22)
    
    pdf.ln(10)
    pdf.set_font('Sarabun', '', 16)
    pdf.cell(0, 10, "แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบ", ln=True, align='C')
    
    pdf.ln(5)
    pdf.set_font('Sarabun', '', 12)
    pdf.cell(0, 8, f"ผู้ส่งมอบ: {st.session_state.s_name}", ln=True)
    pdf.cell(0, 8, f"วันที่: {st.session_state.s_date}", ln=True)

    # รายละเอียดสินค้าตามใบนำส่ง [cite: 1-28]
    for i in range(st.session_state.items_count):
        pdf.ln(5)
        pdf.cell(0, 8, f"รายการที่ {i+1}: {st.session_state.get(f'mat_{i}')} | {st.session_state.get(f'qty_{i}')} KG", ln=True)
        pdf.cell(0, 8, f"ที่อยู่: {st.session_state.get(f't_{i}')} {st.session_state.get(f'a_{i}')} {st.session_state.get(f'p_{i}')}", ln=True)
        
    return pdf.output(dest='S')

# --- 6. ปุ่มดำเนินการ ---
st.write("---")
if st.button("✅ ยืนยันข้อมูลและดาวน์โหลด PDF", type="primary", use_container_width=True):
    if not st.session_state.s_name:
        st.error("กรุณากรอกชื่อผู้ส่งมอบ")
    else:
        pdf_data = generate_pdf()
        if pdf_data:
            # ใช้การ encode แบบ latin-1 ร่วมกับ 'replace' เพื่อป้องกันตัวอักษรพิเศษทำเครื่องค้าง
            st.download_button(
                label="📥 คลิกเพื่อดาวน์โหลด PDF",
                data=pdf_data,
                file_name=f"CPRAM_{st.session_state.s_name}.pdf",
                mime="application/pdf"
            )
        else:
            st.error("ไม่พบไฟล์ฟอนต์ Sarabun-Regular.ttf ในระบบ กรุณาตรวจสอบการอัปโหลดไฟล์ใน GitHub")
