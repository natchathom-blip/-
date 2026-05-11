import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CPRAM - Supplier Form", layout="wide")

st.markdown("""
    <style>
    .header-container { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; margin-bottom: 15px; }
    .logo-box { background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 26px; }
    .doc-id { border: 1.5px solid #000; padding: 4px 12px; font-weight: bold; text-align: center; }
    .section-header { color: #2e7d32; font-size: 20px; font-weight: bold; border-bottom: 2px solid #2e7d32; margin-top: 25px; margin-bottom: 15px; }
    .item-box { background-color: #f1f8e9; padding: 25px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ฟังก์ชันค้นหาและโหลดไฟล์อัตโนมัติ (NEW!) ---
@st.cache_data
def load_address_data():
    # รายชื่อไฟล์ที่ระบบจะพยายามค้นหา
    target_files = ['thailand.xlsx - Sheet1.csv', 'thailand.csv', 'thailand.xlsx']
    
    # วนลูปหาไฟล์ที่มีอยู่ในโฟลเดอร์
    found_file = None
    for f in target_files:
        if os.path.exists(f):
            found_file = f
            break
    
    if found_file:
        try:
            if found_file.endswith('.csv'):
                df = pd.read_csv(found_file)
            else:
                df = pd.read_excel(found_file)
            
            # ล้างช่องว่างหัวตาราง
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"Error reading file {found_file}: {e}")
            return pd.DataFrame()
    else:
        # ถ้าหาไม่เจอเลย จะแสดงคำแนะนำ
        st.error("❌ ไม่พบไฟล์ข้อมูลที่อยู่ (thailand.csv) กรุณาตรวจสอบว่าชื่อไฟล์ถูกต้องและอยู่ในโฟลเดอร์เดียวกับโค้ด")
        return pd.DataFrame()

df_addr = load_address_data()

# --- 3. ส่วนหัว (Header) ---
st.markdown("""
    <div class="header-container">
        <div style="display: flex; align-items: center;">
            <div class="logo-box">cpram</div>
            <div style="margin-left: 15px; color: #2e7d32;">
                <b>CPRAM Co., Ltd.</b><br><small>ระบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ</small>
            </div>
        </div>
        <div style="text-align: right;">
            <div class="doc-id">FR-QAS-10-000</div>
            <div style="font-size: 13px; margin-top: 5px;">มีผลใช้งาน: 2026-05-08</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 4. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ (Lock Data) ---
st.markdown('<div class="section-header">ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="s_date")
s_time = c3.text_input("เวลาส่ง (น.)", placeholder="เช่น 14:00", key="s_time")

c4, c5, c6 = st.columns(3)
s_email = c4.text_input("อีเมลสำหรับรับ PDF *", key="s_email")
recorder = c5.text_input("ลงชื่อผู้กรอก", key="recorder")
origin_main = c6.selectbox("ประเทศแหล่งปลูกหลัก *", ["ประเทศไทย", "จีน", "อื่นๆ"], key="origin_main")

if origin_main == "อื่นๆ":
    origin_other = st.text_input("ระบุชื่อประเทศ *", key="origin_other")
else:
    origin_other = ""

# --- 5. ส่วนที่ 2 — รายการวัตถุดิบ ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

def add_item():
    st.session_state.items_count += 1

st.markdown('<div class="section-header">ส่วนที่ 2 — รายการวัตถุดิบ</div>', unsafe_allow_html=True)

for i in range(st.session_state.items_count):
    st.markdown(f'<div class="item-box">', unsafe_allow_html=True)
    
    col_h, col_del = st.columns([0.8, 0.2])
    col_h.subheader(f"รายการที่ {i+1}")
    
    if st.session_state.items_count > 1 and col_del.button(f"✕ ลบรายการ", key=f"del_{i}"):
        st.session_state.items_count -= 1
        st.rerun()

    # แถวที่ 1-4 (ข้อมูลวัตถุดิบ)
    r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
    r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
    r1c2.text_input("Code", key=f"code_{i}")
    r1c3.number_input("จำนวน (KG) *", min_value=0.0, step=0.1, key=f"qty_{i}")

    r2c1, r2c2, r2c3 = st.columns(3)
    r2c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
    r2c2.text_input("เวลาเก็บเกี่ยว", key=f"ht_{i}")
    r2c3.date_input("วันที่ล้างทำความสะอาด", key=f"cd_{i}")

    r3c1, r3c2, r3c3 = st.columns(3)
    r3c1.text_input("เวลาที่ล้างทำความสะอาด", key=f"ct_{i}")
    r3c2.text_input("ชื่อผู้ปลูก", key=f"grow_{i}")
    r3c3.text_input("เลขที่ GAP", key=f"gap_{i}")

    r4c1, r4c2, r4c3 = st.columns(3)
    r4c1.text_input("รหัสไร่", key=f"farm_{i}")
    r4c2.text_input("ที่อยู่เลขที่", key=f"addr_no_{i}")
    r4c3.text_input("หมู่ที่", key=f"moo_{i}")

    # --- ส่วนที่อยู่แหล่งปลูก (Dropdown จังหวัด/อำเภอ/ตำบล) ---
    st.markdown(f"📍 **ที่อยู่แหล่งปลูก ({origin_main if origin_main != 'อื่นๆ' else origin_other})**")
    a1, a2, a3 = st.columns(3)
    
    if origin_main == "ประเทศไทย":
        if not df_addr.empty:
            # ดึงรายชื่อจังหวัดจากคอลัมน์ชื่อ "จังหวัด"
            p_list = sorted(df_addr["จังหวัด"].unique()) if "จังหวัด" in df_addr.columns else []
            sel_p = a1.selectbox("จังหวัด", ["- เลือก -"] + p_list, key=f"p_{i}")
            
            # ดึงอำเภอ
            amp_opts = sorted(df_addr[df_addr["จังหวัด"] == sel_p]["อำเภอ"].unique()) if sel_p != "- เลือก -" else []
            sel_a = a2.selectbox("อำเภอ", ["- เลือก -"] + amp_opts, key=f"a_{i}")
            
            # ดึงตำบล
            tam_opts = sorted(df_addr[(df_addr["จังหวัด"] == sel_p) & (df_addr["อำเภอ"] == sel_a)]["ตำบล"].unique()) if sel_a != "- เลือก -" else []
            sel_t = a3.selectbox("ตำบล", ["- เลือก -"] + tam_opts, key=f"t_{i}")
        else:
            a1.info("กำลังรอไฟล์ข้อมูลที่อยู่...")
    else:
        # ถ้าไม่ใช่ประเทศไทย ให้กรอกเอง
        a1.text_input("จังหวัด/มณฑล", key=f"p_man_{i}")
        a2.text_input("อำเภอ/เมือง", key=f"a_man_{i}")
        a3.text_input("ตำบล/แขวง", key=f"t_man_{i}")

    # ข้อมูลลักษณะการปลูก (อัปเดตใหม่ตามสั่ง)
    r5c1, r5c2, r5c3, r5c4 = st.columns(4)
    r5c1.text_input("รหัสไปรษณีย์", key=f"z_{i}")
    r5c2.text_input("สายพันธุ์", key=f"breed_{i}")
    r5c3.selectbox("ลักษณะการปลูก", 
                   ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], 
                   key=f"style_{i}")
    r5c4.selectbox("ลักษณะสถานที่ปลูก", ["- เลือก -", "โรงเรือน", "แปลงเปิด"], key=f"loc_{i}")

    st.markdown('</div>', unsafe_allow_html=True)

st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item)

# --- 6. ยืนยันข้อมูล ---
st.write("---")
if st.button("✅ ยืนยันข้อมูลและดาวน์โหลด PDF", type="primary", use_container_width=True):
    if not s_name:
        st.error("กรุณากรอกชื่อผู้ส่งมอบ")
    else:
        st.success("บันทึกข้อมูลเรียบร้อย!")
