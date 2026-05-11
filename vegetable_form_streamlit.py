import streamlit as st
from datetime import datetime, time

# --- 1. CONFIG & STYLE ---
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

# --- 2. SESSION STATE MANAGEMENT (The Fix) ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1  # ใช้ตัวนับแทนการเก็บ List ซับซ้อนป้องกัน Error

def add_item():
    st.session_state.items_count += 1

def remove_item():
    if st.session_state.items_count > 1:
        st.session_state.items_count -= 1

# --- 3. HEADER (ตามรูปภาพ) ---
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

# --- 4. SECTION 1: SUPPLIER INFO ---
st.markdown('<div class="section-header">ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    st.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
    st.date_input("วันที่ส่งวัตถุดิบ *", datetime.now(), key="d_date")
with c2:
    st.time_input("เวลาส่ง *", value=time(14, 0), key="d_time")
    st.text_input("ลงชื่อผู้กรอก", key="recorder")
with c3:
    st.text_input("อีเมลของผู้ส่งมอบ (สำหรับรับ PDF) *", key="s_email")
    country_opt = st.selectbox("ประเทศแหล่งปลูก (หลัก)", ["ไทย", "จีน", "อื่นๆ"], key="c_main")

# --- 5. SECTION 2: MATERIAL ITEMS ---
st.markdown('<div class="section-header">ส่วนที่ 2 — รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด)</div>', unsafe_allow_html=True)

prov_list = ["- เลือก -", "กระบี่", "กรุงเทพมหานคร", "กาญจนบุรี", "กาฬสินธุ์", "กำแพงเพชร", "ขอนแก่น", "จันทบุรี", "ฉะเชิงเทรา", "ชลบุรี", "ชัยนาท", "ชัยภูมิ", "ชุมพร", "เชียงราย", "เชียงใหม่", "ตรัง", "ตราด", "ตาก", "นครนายก", "นครปฐม", "นครพนม", "นครราชสีมา", "นครศรีธรรมราช", "นครสวรรค์", "นนทบุรี", "นราธิวาส", "น่าน", "บึงกาฬ", "บุรีรัมย์", "ปทุมธานี", "ประจวบคีรีขันธ์", "ปราจีนบุรี", "ปัตตานี", "พระนครศรีอยุธยา", "พะเยา", "พังงา", "พัทลุง", "พิจิตร", "พิษณุโลก", "เพชรบุรี", "เพชรบูรณ์", "แพร่", "ภูเก็ต", "มหาสารคาม", "มุกดาหาร", "แม่ฮ่องสอน", "ยโสธร", "ยะลาร้อยเอ็ด", "ระนอง", "ระยอง", "ราชบุรี", "ลพบุรี", "ลำปาง", "ลำพูน", "เลย", "ศรีสะเกษ", "สกลนคร", "สงขลา", "สตูล", "สมุทรปราการ", "สมุทรสงคราม", "สมุทรสาคร", "สระแก้ว", "สระบุรี", "สิงห์บุรี", "สุโขทัย", "สุพรรณบุรี", "สุราษฎร์ธานี", "สุรินทร์", "หนองคาย", "หนองบัวลำภู", "อ่างทอง", "อำนาจเจริญ", "อุดรธานี", "อุตรดิตถ์", "อุทัยธานี", "อุบลราชธานี"]

# วนลูปสร้างฟอร์มตามจำนวนที่เก็บใน items_count
for i in range(st.session_state.items_count):
    with st.container():
        st.markdown(f'<div class="item-box">', unsafe_allow_html=True)
        st.subheader(f"รายการที่ {i+1}")
        
        r1c1, r1c2, r1c3 = st.columns(3)
        r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
        r1c2.text_input("Code (เช่น 721003)", key=f"code_{i}")
        r1c3.number_input("จำนวน (KG) *", min_value=0.0, step=0.1, key=f"qty_{i}")

        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
        r2c2.text_input("เวลาเก็บเกี่ยว", placeholder="08:00", key=f"ht_{i}")
        r2c3.date_input("วันที่ล้างทำความสะอาด", key=f"cd_{i}")

        r3c1, r3c2, r3c3 = st.columns(3)
        r3c1.text_input("เวลาที่ล้างทำความสะอาด", placeholder="08:00-09:30", key=f"ct_{i}")
        r3c2.text_input("ชื่อผู้ปลูก", key=f"grower_{i}")
        r3c3.text_input("เลขที่ GAP", key=f"gap_{i}")

        r4c1, r4c2, r4c3 = st.columns(3)
        r4c1.text_input("รหัสไร่", key=f"farm_{i}")
        r4c2.text_input("ที่อยู่เลขที่ หมู่ที่", key=f"addr_{i}")
        r4c3.selectbox("ประเทศ", ["ไทย", "จีน", "อื่นๆ"], key=f"country_{i}")

        st.markdown("📍 **ที่อยู่แหล่งปลูก**")
        r5c1, r5c2, r5c3 = st.columns(3)
        r5c1.selectbox("จังหวัด/มณฑล", prov_list, key=f"prov_{i}")
        r5c2.selectbox("อำเภอ/เมือง", ["- เลือกจังหวัดก่อน -"], key=f"amp_{i}")
        r5c3.selectbox("ตำบล/เขต", ["- เลือกอำเภอก่อน -"], key=f"tam_{i}")

        r6c1, r6c2, r6c3, r6c4 = st.columns(4)
        r6c1.text_input("รหัสไปรษณีย์", key=f"zip_{i}")
        r6c2.text_input("สายพันธุ์", key=f"breed_{i}")
        r6c3.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
        r6c4.selectbox("ลักษณะสถานที่ปลูก", ["- เลือก -", "โรงเรือน", "แปลงเปิด"], key=f"loc_{i}")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 6. BUTTONS ---
col_b1, col_b2, _ = st.columns([0.2, 0.2, 0.6])
col_b1.button("+ เพิ่มรายการ", on_click=add_item)
col_b2.button("- ลบรายการล่าสุด", on_click=remove_item)

st.write("---")
if st.button("ยืนยันบันทึกข้อมูลและส่ง PDF", type="primary"):
    if not st.session_state.s_name or not st.session_state.s_email:
        st.error("กรุณากรอกชื่อผู้ส่งมอบและอีเมลให้ครบถ้วน")
    else:
        st.success(f"บันทึกข้อมูลเรียบร้อย! ระบบกำลังสร้าง PDF ส่งไปยัง {st.session_state.s_email}")
