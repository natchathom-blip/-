import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# --- 1. SETUP ---
st.set_page_config(page_title="CPRAM Form", layout="wide")

# --- 2. INITIALIZE SESSION STATE (ล็อกข้อมูล) ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

# ฟังก์ชันสำหรับเพิ่มรายการโดยไม่ล้างข้อมูลเดิม
def add_item_callback():
    st.session_state.items_count += 1

# --- 3. LOAD ADDRESS DATA ---
@st.cache_data
def load_address():
    try:
        df = pd.read_excel('thailand.xlsx')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

df_addr = load_address()

# --- 4. HEADER UI ---
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; border-bottom: 3px solid #2e7d32; padding-bottom: 10px;">
        <div style="display: flex; align-items: center;">
            <div style="background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 24px;">cpram</div>
            <div style="margin-left: 15px; color: #2e7d32;"><b>CPRAM Co., Ltd.</b><br><small>ระบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ</small></div>
        </div>
        <div style="text-align: right;">
            <div style="border: 1.5px solid black; padding: 2px 10px;"><b>FR-QAS-10-000</b></div>
            <small>มีผลใช้งาน: 2026-05-08</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 5. FORM INPUTS ---
# ส่วนที่ 1: ข้อมูลผู้ส่งมอบ (ใช้ key ทุุกช่องเพื่อล็อกข้อมูล)
st.subheader("ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ")
c1, c2, c3 = st.columns(3)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="lock_s_name")
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="lock_s_date")
s_time = c3.time_input("เวลาส่ง *", value=time(14, 0), key="lock_s_time")

c4, c5, c6 = st.columns(3)
s_email = c4.text_input("อีเมลสำหรับรับ PDF *", key="lock_s_email")
recorder = c5.text_input("ลงชื่อผู้กรอก", key="lock_recorder")
origin = c6.selectbox("ประเทศแหล่งปลูก", ["ประเทศไทย", "ประเทศจีน", "อื่นๆ"], key="lock_origin")

st.markdown("---")
st.subheader("ส่วนที่ 2 — รายการวัตถุดิบ")

items_data = []
for i in range(st.session_state.items_count):
    with st.expander(f"📦 รายการที่ {i+1}", expanded=True):
        r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
        mat = r1c1.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        code = r1c2.text_input("Code", key=f"code_{i}")
        qty = r1c3.number_input("จำนวน (KG)", key=f"qty_{i}")

        r2c1, r2c2, r2c3, r2c4 = st.columns(4)
        h_date = r2c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
        h_time = r2c2.text_input("เวลาเก็บเกี่ยว", key=f"ht_{i}")
        grower = r2c3.text_input("ชื่อผู้ปลูก", key=f"grower_{i}")
        gap = r2c4.text_input("เลขที่ GAP", key=f"gap_{i}")

        # ส่วนที่อยู่ (ตำบล/อำเภอ/จังหวัด)
        a1, a2, a3, a4 = st.columns(4)
        prov = a1.selectbox("จังหวัด", ["- เลือก -"] + sorted(df_addr['province_th'].unique().tolist()) if not df_addr.empty else [], key=f"p_{i}")
        
        amp_list = sorted(df_addr[df_addr['province_th'] == prov]['district_th'].unique().tolist()) if prov != "- เลือก -" else []
        amp = a2.selectbox("อำเภอ", ["- เลือก -"] + amp_list, key=f"a_{i}")
        
        tam_list = sorted(df_addr[(df_addr['province_th'] == prov) & (df_addr['district_th'] == amp)]['subdistrict_th'].unique().tolist()) if amp != "- เลือก -" else []
        tam = a3.selectbox("ตำบล/เขต", ["- เลือก -"] + tam_list, key=f"t_{i}")
        
        zip_code = ""
        if tam != "- เลือก -":
            zip_code = df_addr[(df_addr['province_th'] == prov) & (df_addr['district_th'] == amp) & (df_addr['subdistrict_th'] == tam)]['postcode'].iloc[0]
        a4.text_input("รหัสไปรษณีย์", value=str(zip_code), key=f"z_{i}", disabled=True)

        items_data.append({'mat': mat, 'code': code, 'qty': qty, 'tam': tam, 'amp': amp, 'prov': prov, 'zip': zip_code})

# --- 6. ACTIONS ---
st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item_callback)

if st.button("ยืนยันข้อมูลและส่ง PDF", type="primary"):
    if not s_name or not s_email:
        st.error("❌ ข้อมูลส่วนที่ 1 ไม่ครบถ้วน (ชื่อ หรือ อีเมล)")
    else:
        # 1. แสดงสถานะทันที
        st.success(f"บันทึกข้อมูลเรียบร้อย! ระบบกำลังประมวลผล PDF ส่งไปยัง {s_email}")
        
        # 2. จำลองปุ่ม Download เพื่อให้ได้ไฟล์ทันที (กันเมลไม่เข้า)
        # pdf_bytes = generate_pdf_logic(items_data) 
        # st.download_button("ดาวน์โหลด PDF
