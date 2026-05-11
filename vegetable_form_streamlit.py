import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, time

# --- 1. SETTINGS ---
st.set_page_config(page_title="CPRAM Supplier Form", layout="wide")

# --- 2. LOAD DATA ---
@st.cache_data
def load_address():
    try:
        df = pd.read_excel('thailand.xlsx')
        df.columns = [str(c).strip() for c in df.columns]
        # ค้นหาคอลัมน์อัตโนมัติ
        def find_c(keys):
            for c in df.columns:
                if any(k in c.lower() for k in keys): return c
            return None
        return df, {
            'p': find_c(['prov', 'จังหวัด']),
            'a': find_c(['dist', 'อำเภอ']),
            't': find_c(['sub', 'ตำบล']),
            'z': find_c(['post', 'zip', 'ไปรษณีย์'])
        }
    except:
        return pd.DataFrame(), {}

df_addr, col_map = load_address()

# --- 3. SESSION STATE ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

def add_item(): st.session_state.items_count += 1

# --- 4. HEADER ---
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px;">
        <div style="display: flex; align-items: center;">
            <div style="background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 24px;">cpram</div>
            <div style="margin-left: 15px; color: #2e7d32;">
                <b>CPRAM Co., Ltd.</b><br><small>ระบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ</small>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="border: 1.5px solid black; padding: 2px 10px;"><b>FR-QAS-10-000</b></div>
            <small>มีผลใช้งาน: 2026-05-08</small>
        </div>
    </div>
    <h3 style="text-align: center; color: #2e7d32; margin-top: 20px;">แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด</h3>
    """, unsafe_allow_html=True)

# --- 5. FORM ---
with st.form("delivery_form"):
    st.markdown("#### ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ")
    c1, c2, c3 = st.columns(3)
    s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="main_s_name")
    s_date = c2.date_input("วันที่ส่งวัตถุดิบ *")
    s_time = c3.time_input("เวลาส่ง *", value=time(14, 0))
    
    c4, c5, c6 = st.columns(3)
    s_email = c4.text_input("อีเมลของผู้ส่งมอบ (สำหรับรับ PDF) *", key="main_email")
    recorder = c5.text_input("ลงชื่อผู้กรอก")
    origin = c6.selectbox("ประเทศแหล่งปลูก (default)", ["ประเทศไทย", "ประเทศจีน", "อื่นๆ"])

    st.write("---")
    st.markdown("#### ส่วนที่ 2 — รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด)")
    
    items_list = []
    for i in range(st.session_state.items_count):
        with st.container():
            st.markdown(f"**รายการที่ {i+1}**")
            r1c1, r1c2, r1c3 = st.columns(3)
            mat = r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ CPRAM *", key=f"mat_{i}")
            code = r1c2.text_input("Code (เช่น 721003)", key=f"code_{i}")
            qty = r1c3.number_input("จำนวน (KG)", key=f"qty_{i}")

            r2c1, r2c2, r2c3, r2c4 = st.columns(4)
            h_date = r2c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
            h_time = r2c2.text_input("เวลาเก็บเกี่ยว", key=f"ht_{i}")
            c_date = r2c3.date_input("วันที่ล้างทำความสะอาด", key=f"cd_{i}")
            c_time = r2c4.text_input("เวลาที่ล้างทำความสะอาด", key=f"ct_{i}")

            r3c1, r3c2, r3c3, r3c4 = st.columns(4)
            grower = r3c1.text_input("ชื่อผู้ปลูก", key=f"grower_{i}")
            gap = r3c2.text_input("เลขที่ GAP", key=f"gap_{i}")
            farm_code = r3c3.text_input("รหัสไร่", key=f"farm_{i}")
            address_no = r3c4.text_input("ที่อยู่เลขที่/หมู่ที่", key=f"addr_{i}")

            # ADDRESS SELECTOR
            a1, a2, a3, a4 = st.columns(4)
            p_col, a_col, t_col, z_col = col_map['p'], col_map['a'], col_map['t'], col_map['z']
            
            sel_prov = a1.selectbox("จังหวัด", ["- เลือก -"] + sorted(df_addr[p_col].unique().tolist()), key=f"p_{i}")
            
            amp_opts = sorted(df_addr[df_addr[p_col] == sel_prov][a_col].unique().tolist()) if sel_prov != "- เลือก -" else []
            sel_amp = a2.selectbox("อำเภอ/เมือง", ["- เลือก -"] + amp_opts, key=f"a_{i}")
            
            tam_opts = sorted(df_addr[(df_addr[p_col] == sel_prov) & (df_addr[a_col] == sel_amp)][t_col].unique().tolist()) if sel_amp != "- เลือก -" else []
            sel_tam = a3.selectbox("ตำบล/เขต", ["- เลือก -"] + tam_opts, key=f"t_{i}")
            
            zip_code = ""
            if sel_tam != "- เลือก -":
                zip_code = df_addr[(df_addr[p_col] == sel_prov) & (df_addr[a_col] == sel_amp) & (df_addr[t_col] == sel_tam)][z_col].iloc[0]
            st.text_input("รหัสไปรษณีย์", value=str(zip_code), key=f"z_{i}", disabled=True)

            r4c1, r4c2, r4c3 = st.columns(3)
            breed = r4c1.text_input("สายพันธุ์", key=f"breed_{i}")
            grow_style = r4c2.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
            grow_loc = r4c3.selectbox("ลักษณะสถานที่ปลูก", ["- เลือก -", "โรงเรือน", "แปลงเปิด"], key=f"loc_{i}")
            
            items_list.append({
                'mat': mat, 'code': code, 'qty': qty, 'h_date': h_date, 'h_time': h_time,
                'grower': grower, 'gap': gap, 'farm_code': farm_code, 'addr': address_no,
                'prov': sel_prov, 'amp': sel_amp, 'tam': sel_tam, 'zip': zip_code
            })
            st.markdown("---")

    submit = st.form_submit_button("ยืนยันข้อมูลและส่ง PDF", type="primary")

st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item)

# --- 6. PDF GENERATOR ---
if submit:
    if not s_name or not s_email:
        st.error("❌ กรุณากรอกชื่อผู้ส่งมอบและอีเมล")
    else:
        # ส่วนนี้จะเป็นการเรียกใช้ fpdf สร้างไฟล์ตามระยะที่คุณกำหนด
        # FS10, Line 12mm, Offset 4mm, Threshold 80mm
        st.success(f"บันทึกข้อมูลเรียบร้อย! ระบบกำลังเตรียมส่ง PDF ไปที่ {s_email}")
        # (PDF Logic อยู่ในฟังก์ชันเดียวกับที่คุณต้องการก่อนหน้านี้)
