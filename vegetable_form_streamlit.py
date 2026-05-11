import streamlit as st
import pandas as pd
from datetime import datetime, time

# --- 1. การตั้งค่าหน้าจอและสไตล์ ---
st.set_page_config(page_title="CPRAM - Supplier Daily Record", layout="wide")

st.markdown("""
    <style>
    .header-container { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; margin-bottom: 15px; }
    .logo-box { background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 26px; font-family: sans-serif; }
    .company-info { color: #2e7d32; line-height: 1.2; margin-left: 15px; }
    .doc-id { border: 1.5px solid #000; padding: 4px 12px; font-weight: bold; font-size: 16px; text-align: center; }
    .section-header { color: #2e7d32; font-size: 20px; font-weight: bold; border-bottom: 2px solid #2e7d32; margin-top: 25px; margin-bottom: 15px; }
    .item-box { background-color: #f1f8e9; padding: 25px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. การจัดการ Session State (แก้ Error บรรทัด 69) ---
# เราต้องมั่นใจว่า items ถูกสร้างขึ้น "ก่อน" โค้ดส่วนอื่นๆ จะทำงาน
if 'items' not in st.session_state:
    st.session_state.items = [{"id": 0}]

def add_item():
    st.session_state.items.append({"id": len(st.session_state.items)})

def remove_item(index):
    if len(st.session_state.items) > 1:
        st.session_state.items.pop(index)

# --- 3. ส่วนหัวแบบฟอร์ม (Header) ---
st.markdown(f"""
    <div class="header-container">
        <div style="display: flex; align-items: center;">
            <div class="logo-box">cpram</div>
            <div class="company-info">
                <div style="font-weight: bold; font-size: 18px;">CPRAM Co., Ltd.</div>
                <div>ระบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ</div>
            </div>
        </div>
        <div style="text-align: right;">
            <div class="doc-id">FR-QAS-10-000</div>
            <div style="font-size: 13px; margin-top: 5px;">มีผลใช้งาน: 2026-05-11</div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 10px;">
        <h2 style="color: #2e7d32;">แบบบันทึกข้อมูลประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด</h2>
    </div>
    """, unsafe_allow_html=True)

# --- 4. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ ---
st.markdown('<div class="section-header">ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    supplier_name = st.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
    delivery_date = st.date_input("วันที่ส่งวัตถุดิบ *", datetime.now(), key="d_date")

with col2:
    delivery_time = st.time_input("เวลาส่ง *", value=time(14, 0), key="d_time")
    recorded_by = st.text_input("ลงชื่อผู้กรอก", key="recorder")

with col3:
    supplier_email = st.text_input("อีเมลของผู้ส่งมอบ (สำหรับรับ PDF) *", key="s_email")
    country_opt = st.selectbox("ประเทศแหล่งปลูก (หลัก)", ["ไทย", "จีน", "อื่นๆ"], key="c_main")
    if country_opt == "อื่นๆ":
        other_country = st.text_input("ระบุประเทศเพิ่มเติม", key="c_other")

# --- 5. ส่วนที่ 2 — รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด) ---
st.markdown('<div class="section-header">ส่วนที่ 2 — รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด)</div>', unsafe_allow_html=True)

province_list = ["- เลือก -", "กระบี่", "กรุงเทพมหานคร", "กาญจนบุรี", "กาฬสินธุ์", "กำแพงเพชร", "ขอนแก่น", "จันทบุรี", "ฉะเชิงเทรา", "ชลบุรี", "ชัยนาท", "ชัยภูมิ", "ชุมพร", "เชียงราย", "เชียงใหม่", "ตรัง", "ตราด", "ตาก", "นครนายก", "นครปฐม", "นครพนม", "นครราชสีมา", "นครศรีธรรมราช", "นครสวรรค์", "นนทบุรี", "นราธิวาส", "น่าน", "บึงกาฬ", "บุรีรัมย์", "ปทุมธานี", "ประจวบคีรีขันธ์", "ปราจีนบุรี", "ปัตตานี", "พระนครศรีอยุธยา", "พะเยา", "พังงา", "พัทลุง", "พิจิตร", "พิษณุโลก", "เพชรบุรี", "เพชรบูรณ์", "แพร่", "ภูเก็ต", "มหาสารคาม", "มุกดาหาร", "แม่ฮ่องสอน", "ยโสธร", "ยะลาร้อยเอ็ด", "ระนอง", "ระยอง", "ราชบุรี", "ลพบุรี", "ลำปาง", "ลำพูน", "เลย", "ศรีสะเกษ", "สกลนคร", "สงขลา", "สตูล", "สมุทรปราการ", "สมุทรสงคราม", "สมุทรสาคร", "สระแก้ว", "สระบุรี", "สิงห์บุรี", "สุโขทัย", "สุพรรณบุรี", "สุราษฎร์ธานี", "สุรินทร์", "หนองคาย", "หนองบัวลำภู", "อ่างทอง", "อำนาจเจริญ", "อุดรธานี", "อุตรดิตถ์", "อุทัยธานี", "อุบลราชธานี"]

# เช็ค Safety ก่อนรัน Loop
if "items" in st.session_state:
    for i, item in enumerate(st.session_state.items):
        with st.container():
            st.markdown(f'<div class="item-box">', unsafe_allow_html=True)
            h_col1, h_col2 = st.columns([0.85, 0.15])
            h_col1.subheader(f"รายการที่ {i+1}")
            h_col2.button(f"✕ ลบรายการ", key=f"del_{i}", on_click=remove_item, args=(i,))

            # แถวที่ 1
            r1c1, r1c2, r1c3 = st.columns(3)
            r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
            r1c2.text_input("Code", placeholder="เช่น 721003", key=f"code_{i}")
            r1c3.number_input("จำนวน (KG) *", min_value=0.0, step=0.1, key=f"qty_{i}")

            # แถวที่ 2
            r2c1, r2c2, r2c3 = st.columns(3)
            r2c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
            r2c2.text_input("เวลาเก็บเกี่ยว", placeholder="เช่น 08:00", key=f"ht_{i}")
            r2c3.date_input("วันที่ล้างทำความสะอาด", key=f"cd_{i}")

            # แถวที่ 3
            r3c1, r3c2, r3c3 = st.columns(3)
            r3c1.text_input("เวลาที่ล้างทำความสะอาด", placeholder="เช่น 08:00-09:30", key=f"ct_{i}")
            r3c2.text_input("ชื่อผู้ปลูก", key=f"grower_{i}")
            r3c3.text_input("เลขที่ GAP", key=f"gap_{i}")

            # แถวที่ 4
            r4c1, r4c2, r4c3 = st.columns(3)
            r4c1.text_input("รหัสไร่", key=f"farm_{i}")
            r4c2.text_input("ที่อยู่เลขที่ หมู่ที่", key=f"addr_{i}")
            r4c3.selectbox("ประเทศ", ["ไทย", "จีน", "อื่นๆ"], key=f"country_{i}")

            # ที่อยู่ (Dropdown)
            st.markdown("📍 **ที่อยู่แหล่งปลูก**")
            r5c1, r5c2, r5c3 = st.columns(3)
            r5c1.selectbox("จังหวัด/มณฑล", province_list, key=f"prov_{i}")
            r5c2.selectbox("อำเภอ/เมือง", ["- เลือกจังหวัดก่อน -"], key=f"amp_{i}")
            r5c3.selectbox("ตำบล/เขต", ["- เลือกอำเภอก่อน -"], key=f"tam_{i}")

            # แถวสุดท้าย
            r6c1, r6c2, r6c3, r6c4 = st.columns(4)
            r6c1.text_input("รหัสไปรษณีย์", key=f"zip_{i}")
            r6c2.text_input("สายพันธุ์", key=f"breed_{i}")
            r6c3.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
            r6c4.selectbox("ลักษณะสถานที่ปลูก", ["- เลือก -", "โรงเรือน", "แปลงเปิด"], key=f"loc_{i}")

            st.markdown('</div>', unsafe_allow_html=True)

# ปุ่มเพิ่มรายการ (อยู่นอก Loop)
st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item)

# --- 6. ปุ่มบันทึกข้อมูล ---
st.write("---")
if st.button("ยืนยันบันทึกข้อมูลและส่ง PDF", type="primary"):
    if not supplier_name or not supplier_email:
        st.error("กรุณากรอกข้อมูลส่วนที่ 1 ให้ครบถ้วนก่อนส่ง")
    else:
        st.success("บันทึกข้อมูลสำเร็จ! ระบบกำลังเตรียมส่งไฟล์ PDF...")
