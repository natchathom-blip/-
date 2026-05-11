import streamlit as st
import pandas as pd
import os

# --- ส่วนการโหลดข้อมูลที่อยู่ ---
@st.cache_data
def load_address_data():
    file_path = 'thailand.xlsx'
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        # ทำความสะอาดข้อมูลเพื่อป้องกัน Error
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    return pd.DataFrame()

df_addr = load_address_data()

# จัดการจำนวนรายการใน Session State
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

st.markdown("#### <span style='color: #2e7d32;'>ส่วนที่ 2 — รายการวัตถุดิบ</span> <span style='font-size: 12px; color: #999;'>(เพิ่มได้ไม่จำกัด)</span>", unsafe_allow_html=True)

# วนลูปสร้างรายการตามจำนวน items_count
for i in range(st.session_state.items_count):
    # ใช้ st.container ร่วมกับ CSS เพื่อสร้างกรอบเหมือน image_89a0d7.png
    st.markdown(f"""
        <div style='background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 15px;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <b style='color: #2e7d32; font-size: 18px;'>รายการที่ {i+1}</b>
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.container():
        # แถวที่ 1: ชนิดวัตถุดิบ, Code, จำนวน
        r1_c1, r1_c2, r1_c3 = st.columns([2, 1, 1])
        r1_c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
        r1_c2.text_input("Code", placeholder="เช่น 71000277", key=f"code_{i}")
        r1_c3.number_input("จำนวน (KG) *", min_value=0.0, format="%.2f", key=f"qty_{i}")

        # แถวที่ 2: วัน/เวลาเก็บเกี่ยว และ วันที่ล้าง
        r2_c1, r2_c2, r2_c3 = st.columns(3)
        r2_c1.date_input("วันที่เก็บเกี่ยว", key=f"h_date_{i}")
        r2_c2.text_input("เวลาเก็บเกี่ยว", placeholder="เช่น 08:00", key=f"h_time_{i}")
        r2_c3.date_input("วันที่ล้างทำความสะอาด", key=f"c_date_{i}")

        # แถวที่ 3: เวลาล้าง, ชื่อผู้ปลูก, GAP
        r3_c1, r3_c2, r3_c3 = st.columns(3)
        r3_c1.text_input("เวลาที่ล้างทำความสะอาด", placeholder="เช่น 08:00 หรือ 08:00-09:30", key=f"c_time_{i}")
        r3_c2.text_input("ชื่อผู้ปลูก", key=f"grower_{i}")
        r3_c3.text_input("เลขที่ GAP", key=f"gap_{i}")

        # แถวที่ 4: รหัสไร่, เลขที่, หมู่ที่
        r4_c1, r4_c2, r4_c3 = st.columns(3)
        r4_c1.text_input("รหัสไร่", key=f"farm_id_{i}")
        r4_c2.text_input("ที่อยู่เลขที่", key=f"addr_no_{i}")
        r4_c3.text_input("หมู่ที่", key=f"moo_{i}")

        # --- 📍 ส่วนที่อยู่แหล่งปลูก (Cascading Dropdown) ---
        st.markdown("📍 **ที่อยู่แหล่งปลูก (cascading dropdown)**")
        a1, a2, a3, a4 = st.columns(4)
        
        country = a1.selectbox("ประเทศ", ["ไทย", "จีน", "อื่นๆ"], key=f"country_{i}")
        
        selected_zip = ""
        if country == "ไทย" and not df_addr.empty:
            # 1. จังหวัด
            prov_list = sorted(df_addr["จังหวัด"].unique().tolist())
            province = a2.selectbox("จังหวัด/มณฑล", ["- เลือก -"] + prov_list, key=f"prov_{i}")
            
            # 2. อำเภอ (กรองตามจังหวัด)
            dist_list = []
            if province != "- เลือก -":
                dist_list = sorted(df_addr[df_addr["จังหวัด"] == province]["อำเภอ"].unique().tolist())
            district = a3.selectbox("อำเภอ/เมือง", ["- เลือก -"] + dist_list, key=f"dist_{i}")
            
            # 3. ตำบล (กรองตามจังหวัดและอำเภอ)
            sub_list = []
            if district != "- เลือก -":
                sub_list = sorted(df_addr[(df_addr["จังหวัด"] == province) & (df_addr["อำเภอ"] == district)]["ตำบล"].unique().tolist())
            sub_dist = a4.selectbox("ตำบล/เขต", ["- เลือก -"] + sub_list, key=f"sub_{i}")

            # 4. ดึงรหัสไปรษณีย์อัตโนมัติ (หากมีในไฟล์)
            if sub_dist != "- เลือก -":
                z_match = df_addr[(df_addr["จังหวัด"] == province) & 
                                 (df_addr["อำเภอ"] == district) & 
                                 (df_addr["ตำบล"] == sub_dist)]["รหัสไปรษณีย์"].values
                if len(z_match) > 0: selected_zip = str(z_match[0])
        else:
            a2.text_input("จังหวัด/มณฑล", key=f"prov_manual_{i}")
            a3.text_input("อำเภอ/เมือง", key=f"dist_manual_{i}")
            a4.text_input("ตำบล/เขต", key=f"sub_manual_{i}")

        # แถวสุดท้าย: รหัสไปรษณีย์, สายพันธุ์, ลักษณะการปลูก
        f1, f2, f3, f4 = st.columns(4)
        f1.text_input("รหัสไปรษณีย์", value=selected_zip, key=f"zip_{i}")
        f2.text_input("สายพันธุ์", key=f"breed_{i}")
        f3.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
        f4.selectbox("ลักษณะสถานที่ปลูก", ["- เลือก -", "โรงเรือน", "แปลงเปิด"], key=f"place_{i}")
        st.markdown("---")

# ปุ่มเพิ่มรายการ
if st.button("+ เพิ่มรายการวัตถุดิบ", use_container_width=True):
    st.session_state.items_count += 1
    st.rerun()
