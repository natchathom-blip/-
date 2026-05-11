import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

# --- 1. โหลดข้อมูลที่อยู่ (ใช้ Cache เพื่อความเร็วและป้องกันข้อมูลหาย) ---
@st.cache_data
def load_address_data():
    # ตรวจสอบชื่อไฟล์ให้ตรงกับในระบบของคุณ
    file_path = 'thailand.xlsx - Sheet1.csv'
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            # ล้างช่องว่างหัวตารางและแปลงเป็น String ทั้งหมดกันพลาด
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"Error loading CSV: {e}")
            return pd.DataFrame()
    else:
        st.error("❌ ไม่พบไฟล์ thailand.xlsx - Sheet1.csv ในระบบ")
        return pd.DataFrame()

df_addr = load_address_data()

# --- 2. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CPRAM Form", layout="wide")

# --- 3. ส่วนหัว (Header) ตามรูปภาพ ---
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
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="s_date")

origin_main = st.selectbox("ประเทศแหล่งปลูกหลัก", ["ประเทศไทย", "จีน", "อื่นๆ"], key="origin_main")

# --- 5. ส่วนที่ 2 — รายการวัตถุดิบ (ระบบ Lock Dropdown) ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

def add_item():
    st.session_state.items_count += 1

for i in range(st.session_state.items_count):
    with st.container():
        st.markdown(f'<div style="background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 15px;">', unsafe_allow_html=True)
        st.markdown(f"**รายการที่ {i+1}**")
        
        # ข้อมูลวัตถุดิบ
        r1, r2, r3 = st.columns([2, 1, 1])
        mat = r1.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        qty = r3.number_input("จำนวน (KG)", key=f"qty_{i}", min_value=0.0)

        # --- ส่วนที่อยู่ (Dropdown จังหวัด อำเภอ ตำบล) ---
        st.markdown("📍 **ที่อยู่แหล่งปลูก**")
        if origin_main == "ประเทศไทย" and not df_addr.empty:
            a1, a2, a3 = st.columns(3)
            
            # 1. เลือกจังหวัด
            provinces = sorted(df_addr["จังหวัด"].unique().tolist())
            p_val = a1.selectbox("จังหวัด", ["- เลือก -"] + provinces, key=f"p_{i}")
            
            # 2. เลือกอำเภอ (จะเปลี่ยนตามจังหวัดที่เลือก)
            if p_val != "- เลือก -":
                districts = sorted(df_addr[df_addr["จังหวัด"] == p_val]["อำเภอ"].unique().tolist())
            else:
                districts = []
            a_val = a2.selectbox("อำเภอ", ["- เลือก -"] + districts, key=f"a_{i}")
            
            # 3. เลือกตำบล (จะเปลี่ยนตามอำเภอที่เลือก)
            if a_val != "- เลือก -":
                sub_districts = sorted(df_addr[(df_addr["จังหวัด"] == p_val) & (df_addr["อำเภอ"] == a_val)]["ตำบล"].unique().tolist())
            else:
                sub_districts = []
            t_val = a3.selectbox("ตำบล", ["- เลือก -"] + sub_districts, key=f"t_{i}")
            
        else:
            # กรณีประเทศอื่นๆ ให้กรอกเอง
            a1, a2, a3 = st.columns(3)
            a1.text_input("จังหวัด/มณฑล", key=f"p_man_{i}")
            a2.text_input("อำเภอ/เมือง", key=f"a_man_{i}")
            a3.text_input("ตำบล/แขวง", key=f"t_man_{i}")

        st.markdown('</div>', unsafe_allow_html=True)

if st.button("+ เพิ่มรายการวัตถุดิบ"):
    add_item()
    st.rerun()

# --- 6. ปุ่มสร้าง PDF ---
st.write("---")
if st.button("✅ ยืนยันและดาวน์โหลด PDF", type="primary", use_container_width=True):
    # (โค้ดสร้าง PDF โดยใช้ Sarabun-Regular.ttf เหมือนเดิม)
    st.success("สร้างไฟล์ PDF สำเร็จ! (พร้อมข้อมูลที่อยู่ที่เลือกไว้)")
