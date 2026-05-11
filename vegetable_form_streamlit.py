import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# --- 1. ตั้งค่าพื้นฐานและโหลดข้อมูล ---
st.set_page_config(page_title="CPRAM Digital Form", layout="wide")

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

@st.cache_data
def load_address_data():
    file_path = 'thailand.xlsx' #
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        # ล้างข้อมูลช่องว่างเพื่อให้เปรียบเทียบค่าได้แม่นยำ
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    return pd.DataFrame()

df_addr = load_address_data()

# จัดการรายการวัตถุดิบด้วย List ใน Session State เพื่อป้องกัน TypeError
if 'item_ids' not in st.session_state:
    st.session_state.item_ids = [0]
if 'next_id' not in st.session_state:
    st.session_state.next_id = 1

# --- 2. ส่วนหัว (Header) ตามมาตรฐาน FR-QAS ---
# ค้นหาคำว่า header_html = f""" ไปจนถึงเครื่องหมาย """
header_html = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #2e7d32; padding-bottom: 10px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center;">
            {f'<img src="data:image/png;base64,{logo_base64}" width="140">' if logo_base64 else ''}
            <div style="margin-left: 15px;">
                <b style="font-size: 22px; color: #2e7d32; line-height: 1;">CPRAM Co., Ltd.</b><br>
                <span style="font-size: 16px; color: #444;">ระบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ</span>
            </div>
        </div>
        <div style="text-align: right; line-height: 1.2;">
            <b style="font-size: 18px; color: #333;">FR-QAS-10-000</b><br>
            <span style="font-size: 14px; color: #666;">มีผลใช้งาน: 2026-05-08</span>
        </div>
    </div>
"""
st.markdown(header_html, unsafe_allow_html=True) #

st.markdown("<h3 style='text-align: center; color: #2e7d32;'>แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>กรุณากรอกข้อมูลให้ครบถ้วน — เลือก จังหวัด/อำเภอ/ตำบล จาก dropdown ระบบจะกรอกรหัสไปรษณีย์ให้อัตโนมัติ</p>", unsafe_allow_html=True)

# --- 3. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ ---
st.markdown("#### <span style='color: #2e7d32;'>ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ</span>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
supplier = c1.text_input("ผู้ส่งมอบ (Supplier) *")
d_date = c2.date_input("วันที่ส่งวัตถุดิบ *", value=datetime.now())
d_time = c3.text_input("เวลาส่ง", placeholder="เช่น 14:00 น.")

c4, c5, c6 = st.columns(3)
email = c4.text_input("อีเมลของผู้ส่งมอบ (สำหรับรับ PDF) *")
recorder = c5.text_input("ลงชื่อผู้กรอก")
origin_def = c6.selectbox("ประเทศแหล่งปลูก (default)", ["ประเทศไทย", "จีน", "อื่นๆ"])

# --- 4. ส่วนที่ 2 — รายการวัตถุดิบ ---
st.markdown("#### <span style='color: #2e7d32;'>ส่วนที่ 2 — รายการวัตถุดิบ</span> <span style='font-size: 12px; color: #999;'>(เพิ่มได้ไม่จำกัด)</span>", unsafe_allow_html=True)

for index, i in enumerate(st.session_state.item_ids):
    with st.container():
        # สร้างกรอบและปุ่มลบ
        header_col, del_col = st.columns([5, 1])
        header_col.markdown(f"**รายการที่ {index + 1}**")
        if del_col.button("✕ ลบรายการนี้", key=f"del_{i}", use_container_width=True):
            if len(st.session_state.item_ids) > 1:
                st.session_state.item_ids.remove(i)
                st.rerun()

        # แถวข้อมูลหลัก
        r1, r2, r3 = st.columns([2, 1, 1])
        r1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
        r2.text_input("Code", placeholder="เช่น 71000277", key=f"code_{i}")
        r3.number_input("จำนวน (KG) *", min_value=0.0, format="%.2f", key=f"qty_{i}")

        r4, r5, r6 = st.columns(3)
        r4.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
        r5.text_input("เวลาเก็บเกี่ยว", placeholder="เช่น 08:00", key=f"ht_{i}")
        r6.date_input("วันที่ล้างทำความสะอาด", key=f"cd_{i}")

        r7, r8, r9 = st.columns(3)
        r7.text_input("เวลาที่ล้างทำความสะอาด", placeholder="เช่น 08:00 หรือ 08:00-09:30", key=f"ct_{i}")
        r8.text_input("ชื่อผู้ปลูก", key=f"grower_{i}")
        r9.text_input("เลขที่ GAP", key=f"gap_{i}")

        r10, r11, r12 = st.columns(3)
        r10.text_input("รหัสไร่", key=f"farm_{i}")
        r11.text_input("ที่อยู่เลขที่", key=f"addr_{i}")
        r12.text_input("หมู่ที่", key=f"moo_{i}")

        # --- 📍 ส่วนที่อยู่แหล่งปลูก Cascading Dropdown ---
        st.markdown("📍 **ที่อยู่แหล่งปลูก (cascading dropdown)**")
        a1, a2, a3, a4 = st.columns(4)
        
        country = a1.selectbox("ประเทศ", ["ไทย", "จีน", "อื่นๆ"], key=f"cntry_{i}")
        zip_auto = ""
        
        if country == "ไทย" and not df_addr.empty:
            prov_list = sorted(df_addr["จังหวัด"].unique().tolist())
            province = a2.selectbox("จังหวัด/มณฑล", ["- เลือก -"] + prov_list, key=f"prov_{i}")
            
            dist_list = []
            if province != "- เลือก -":
                dist_list = sorted(df_addr[df_addr["จังหวัด"] == province]["อำเภอ"].unique().tolist())
            district = a3.selectbox("อำเภอ/เมือง", ["- เลือก -"] + dist_list, key=f"dist_{i}")
            
            sub_list = []
            if district != "- เลือก -":
                sub_list = sorted(df_addr[(df_addr["จังหวัด"] == province) & (df_addr["อำเภอ"] == district)]["ตำบล"].unique().tolist())
            sub_dist = a4.selectbox("ตำบล/เขต", ["- เลือก -"] + sub_list, key=f"sub_{i}")

            # ดึงรหัสไปรษณีย์อัตโนมัติ
            if sub_dist != "- เลือก -":
                z_match = df_addr[(df_addr["จังหวัด"] == province) & (df_addr["อำเภอ"] == district) & (df_addr["ตำบล"] == sub_dist)]
                if not z_match.empty and "รหัสไปรษณีย์" in df_addr.columns:
                    zip_auto = str(z_match["รหัสไปรษณีย์"].values[0])
        else:
            a2.text_input("จังหวัด/มณฑล", key=f"prov_m_{i}")
            a3.text_input("อำเภอ/เมือง", key=f"dist_m_{i}")
            a4.text_input("ตำบล/เขต", key=f"sub_m_{i}")

        # แถวสุดท้ายของรายการ
        f1, f2, f3, f4 = st.columns(4)
        f1.text_input("รหัสไปรษณีย์", value=zip_auto, key=f"zip_{i}")
        f2.text_input("สายพันธุ์", key=f"breed_{i}")
        f3.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
        f4.selectbox("ลักษณะสถานที่ปลูก", ["- เลือก -", "ระบบเปิด", "ระบบปิด"], key=f"place_{i}")
        st.markdown("<hr style='border: 1px dashed #2e7d32;'>", unsafe_allow_html=True)

# --- 5. ปุ่มเพิ่มรายการและบันทึก ---
if st.button("+ เพิ่มรายการวัตถุดิบ", use_container_width=True):
    st.session_state.item_ids.append(st.session_state.next_id)
    st.session_state.next_id += 1
    st.rerun()

if st.button("✅ ยืนยันและตรวจสอบข้อมูล", type="primary", use_container_width=True):
    if not supplier or not email:
        st.error("กรุณากรอกข้อมูลสำคัญ (เครื่องหมาย *) ให้ครบถ้วน")
    else:
        st.success("บันทึกข้อมูลเรียบร้อย!")
