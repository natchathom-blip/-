import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CPRAM Digital Form", layout="wide")

# --- 2. ฟังก์ชันช่วยจัดการรูปภาพ (ต้องอยู่ก่อนการเรียกใช้ header_html) ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# โหลดข้อมูลที่อยู่
@st.cache_data
def load_address_data():
    file_path = 'thailand.xlsx'
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    return pd.DataFrame()

df_addr = load_address_data()

# จัดการ State ของรายการวัตถุดิบ
if 'item_ids' not in st.session_state:
    st.session_state.item_ids = [0]
if 'next_id' not in st.session_state:
    st.session_state.next_id = 1

# --- 3. ส่วนหัว (Header) แก้ไขตามรูปแบบ image_891df3.png ---
logo_base64 = get_image_base64("image_9482bc.png") 

header_html = f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #2e7d32; padding-bottom: 10px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center;">
            {f'<img src="data:image/png;base64,{logo_base64}" width="120">' if logo_base64 else ''}
            <div style="margin-left: 15px;">
                <b style="font-size: 20px; color: #2e7d32; line-height: 1.2;">CPRAM Co., Ltd.</b><br>
                <span style="font-size: 14px; color: #444;">ระบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ</span>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="border: 1.5px solid #333; padding: 5px 15px; display: inline-block; font-weight: bold; font-size: 18px; letter-spacing: 1px;">
                FR-QAS-10-000
            </div>
        </div>
    </div>
"""
st.markdown(header_html, unsafe_allow_html=True)
"""
st.markdown(header_html, unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center; color: #2e7d32;'>แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด</h3>", unsafe_allow_html=True) #
st.markdown("<p style='text-align: center; color: #666;'>กรุณากรอกข้อมูลให้ครบถ้วน — เลือก จังหวัด/อำเภอ/ตำบล จาก dropdown ระบบจะกรอกรหัสไปรษณีย์ให้อัตโนมัติ</p>", unsafe_allow_html=True) #

# --- 4. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ ---
st.markdown("#### <span style='color: #2e7d32;'>ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ</span>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
supplier = c1.text_input("ผู้ส่งมอบ (Supplier) *")
d_date = c2.date_input("วันที่ส่งวัตถุดิบ *", value=datetime.now())
d_time = c3.text_input("เวลาส่ง", placeholder="เช่น 14:00 น.")

c4, c5, c6 = st.columns(3)
email = c4.text_input("อีเมลของผู้ส่งมอบ (สำหรับรับ PDF) *")
recorder = c5.text_input("ลงชื่อผู้กรอก")
origin_def = c6.selectbox("ประเทศแหล่งปลูก (default)", ["ประเทศไทย", "จีน", "อื่นๆ"])

# --- 5. ส่วนที่ 2 — รายการวัตถุดิบ ---
st.markdown("#### <span style='color: #2e7d32;'>ส่วนที่ 2 — รายการวัตถุดิบ</span>", unsafe_allow_html=True)

for index, i in enumerate(st.session_state.item_ids):
    with st.container():
        # แถบหัวรายการและปุ่มลบ
        h_col, d_col = st.columns([5, 1])
        h_col.markdown(f"**รายการที่ {index + 1}**")
        if d_col.button("✕ ลบรายการนี้", key=f"del_{i}", use_container_width=True):
            if len(st.session_state.item_ids) > 1:
                st.session_state.item_ids.remove(i)
                st.rerun()

        # รายละเอียดข้อมูลวัตถุดิบ
        r1, r2, r3 = st.columns([2, 1, 1])
        r1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
        r2.text_input("Code", key=f"code_{i}")
        r3.number_input("จำนวน (KG) *", min_value=0.0, key=f"qty_{i}")

        r4, r5, r6 = st.columns(3)
        r4.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
        r5.text_input("เวลาเก็บเกี่ยว", key=f"ht_{i}")
        r6.date_input("วันที่ล้างทำความสะอาด", key=f"cd_{i}")

        r7, r8, r9 = st.columns(3)
        r7.text_input("เวลาที่ล้างทำความสะอาด", key=f"ct_{i}")
        r8.text_input("ชื่อผู้ปลูก", key=f"grower_{i}")
        r9.text_input("เลขที่ GAP", key=f"gap_{i}")

        r10, r11, r12 = st.columns(3)
        r10.text_input("รหัสไร่", key=f"farm_{i}")
        r11.text_input("ที่อยู่เลขที่", key=f"addr_{i}")
        r12.text_input("หมู่ที่", key=f"moo_{i}")

        # ที่อยู่แหล่งปลูก Cascading Dropdown
        st.markdown("📍 **ที่อยู่แหล่งปลูก (cascading dropdown)**")
        a1, a2, a3, a4 = st.columns(4)
        country = a1.selectbox("ประเทศ", ["ไทย", "จีน", "อื่นๆ"], key=f"cnt_{i}")
        
        zip_auto = ""
        if country == "ไทย" and not df_addr.empty:
            p_list = sorted(df_addr["จังหวัด"].unique().tolist())
            province = a2.selectbox("จังหวัด/มณฑล", ["- เลือก -"] + p_list, key=f"p_{i}")
            
            d_list = []
            if province != "- เลือก -":
                d_list = sorted(df_addr[df_addr["จังหวัด"] == province]["อำเภอ"].unique().tolist())
            district = a3.selectbox("อำเภอ/เมือง", ["- เลือก -"] + d_list, key=f"d_{i}")
            
            t_list = []
            if district != "- เลือก -":
                t_list = sorted(df_addr[(df_addr["จังหวัด"] == province) & (df_addr["อำเภอ"] == district)]["ตำบล"].unique().tolist())
            sub_dist = a4.selectbox("ตำบล/เขต", ["- เลือก -"] + t_list, key=f"t_{i}")

            if sub_dist != "- เลือก -":
                z_match = df_addr[(df_addr["จังหวัด"] == province) & (df_addr["อำเภอ"] == district) & (df_addr["ตำบล"] == sub_dist)]
                if not z_match.empty: zip_auto = str(z_match["รหัสไปรษณีย์"].values[0])
        else:
            a2.text_input("จังหวัด/มณฑล", key=f"p_m_{i}")
            a3.text_input("อำเภอ/เมือง", key=f"d_m_{i}")
            a4.text_input("ตำบล/เขต", key=f"t_m_{i}")

        # แก้ไขจุดที่ 2: เปลี่ยนเป็น ระบบเปิด / ระบบปิด
        f1, f2, f3, f4 = st.columns(4)
        f1.text_input("รหัสไปรษณีย์", value=zip_auto, key=f"zip_{i}")
        f2.text_input("สายพันธุ์", key=f"breed_{i}")
        f3.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
        f4.selectbox("ลักษณะสถานที่ปลูก", ["- เลือก -", "ระบบเปิด", "ระบบปิด"], key=f"place_{i}") # แก้ไขตรงนี้
        st.markdown("<hr style='border: 1px dashed #2e7d32;'>", unsafe_allow_html=True)

# --- 6. ปุ่มดำเนินการ ---
if st.button("+ เพิ่มรายการวัตถุดิบ", use_container_width=True):
    st.session_state.item_ids.append(st.session_state.next_id)
    st.session_state.next_id += 1
    st.rerun()

if st.button("✅ ยืนยันข้อมูล", type="primary", use_container_width=True):
    st.success("บันทึกข้อมูลเรียบร้อย!")
