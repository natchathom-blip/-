import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- ส่วนโหลดข้อมูล ---
@st.cache_data
def load_address_data():
    file_path = 'thailand.xlsx'
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        # ทำความสะอาดข้อมูลช่องว่าง
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    return pd.DataFrame()

df_addr = load_address_data()

# --- ตรวจสอบ Session State เพื่อป้องกัน TypeError ---
if 'items' not in st.session_state:
    st.session_state.items = 1

# ... (ส่วน Header และ ส่วนที่ 1 ตามที่เคยทำไว้) ...

# --- ส่วนที่ 2 — รายการวัตถุดิบ ---
st.markdown("#### ส่วนที่ 2 — รายการวัตถุดิบ")

for i in range(st.session_state.items):
    with st.container():
        st.write(f"**รายการที่ {i+1}**")
        
        # ฟิลด์ข้อมูลทั่วไป
        c1, c2, c3 = st.columns(3)
        c1.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        c2.text_input("Code", key=f"code_{i}", placeholder="71000277")
        c3.number_input("จำนวน (KG) *", key=f"qty_{i}", step=0.01)

        # ส่วนที่อยู่แหล่งปลูก (Cascading Dropdown)
        st.markdown("📍 **ที่อยู่แหล่งปลูก (Cascading Dropdown)**")
        a1, a2, a3, a4 = st.columns(4)
        
        # 1. เลือกจังหวัด
        prov_list = sorted(df_addr["จังหวัด"].unique().tolist()) if not df_addr.empty else []
        province = a1.selectbox("จังหวัด/มณฑล", ["- เลือก -"] + prov_list, key=f"prov_{i}")
        
        # 2. เลือกอำเภอ (กรองตามจังหวัด)
        dist_list = []
        if province != "- เลือก -":
            dist_list = sorted(df_addr[df_addr["จังหวัด"] == province]["อำเภอ"].unique().tolist())
        district = a2.selectbox("อำเภอ/เมือง", ["- เลือก -"] + dist_list, key=f"dist_{i}")
        
        # 3. เลือกตำบล (กรองตามอำเภอ)
        sub_list = []
        if district != "- เลือก -":
            sub_list = sorted(df_addr[(df_addr["จังหวัด"] == province) & (df_addr["อำเภอ"] == district)]["ตำบล"].unique().tolist())
        sub_dist = a3.selectbox("ตำบล/เขต", ["- เลือก -"] + sub_list, key=f"sub_{i}")

        # 4. ดึงรหัสไปรษณีย์อัตโนมัติ (ถ้ามีในไฟล์)
        zip_code = ""
        if sub_dist != "- เลือก -" and "รหัสไปรษณีย์" in df_addr.columns:
            zip_val = df_addr[(df_addr["จังหวัด"] == province) & 
                             (df_addr["อำเภอ"] == district) & 
                             (df_addr["ตำบล"] == sub_dist)]["รหัสไปรษณีย์"].values
            zip_code = str(zip_val[0]) if len(zip_val) > 0 else ""
        
        a4.text_input("รหัสไปรษณีย์", value=zip_code, key=f"zip_{i}")

        # ฟิลด์ข้อมูลเพิ่มเติมท้ายรายการ
        b1, b2, b3 = st.columns(3)
        b1.text_input("สายพันธุ์", key=f"breed_{i}")
        b2.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกดินยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"type_{i}")
        b3.selectbox("ลักษณะสถานที่ปลูก", ["- เลือก -", "โรงเรือน", "แปลงเปิด"], key=f"place_{i}")
        st.markdown("---")

if st.button("+ เพิ่มรายการวัตถุดิบ"):
    st.session_state.items += 1
    st.rerun()
