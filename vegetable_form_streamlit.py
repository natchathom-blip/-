import streamlit as st
import pandas as pd
import os
from fpdf import FPDF

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CPRAM Supplier Form", layout="wide")

# --- 2. ฟังก์ชันโหลดข้อมูลที่อยู่ (ปรับปรุงการดึงคอลัมน์) ---
@st.cache_data
def load_address_data():
    file_path = 'thailand.xlsx - Sheet1.csv'
    if os.path.exists(file_path):
        try:
            # ลองโหลดไฟล์
            df = pd.read_csv(file_path)
            # ล้างช่องว่างที่ชื่อคอลัมน์เพื่อป้องกัน Error
            df.columns = [str(c).strip() for c in df.columns]
            
            # ตรวจสอบว่ามีคอลัมน์ที่ต้องการไหม ถ้าไม่มีให้ลองเปลี่ยนชื่อ
            col_map = {
                'จังหวัด': ['จังหวัด', 'province', 'Province', 'PROVINCE'],
                'อำเภอ': ['อำเภอ', 'amphoe', 'district', 'District'],
                'ตำบล': ['ตำบล', 'tambon', 'subdistrict', 'Subdistrict']
            }
            
            for standard, aliases in col_map.items():
                for alias in aliases:
                    if alias in df.columns and standard not in df.columns:
                        df.rename(columns={alias: standard}, inplace=True)
            
            return df
        except Exception as e:
            st.error(f"โหลดไฟล์ไม่ได้: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

df_addr = load_address_data()

# --- ตรวจสอบสถานะไฟล์ (Debug) ---
if df_addr.empty:
    st.error("⚠️ ไม่พบข้อมูลที่อยู่ในไฟล์ 'thailand.xlsx - Sheet1.csv' กรุณาตรวจสอบชื่อไฟล์ใน GitHub")
else:
    st.success(f"✅ โหลดข้อมูลที่อยู่สำเร็จ (พบ {len(df_addr)} แถว)")

# --- 3. ส่วนหัว Header (ตามรูปภาพ) ---
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; margin-bottom: 20px;">
        <div style="background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 26px;">cpram</div>
        <div style="text-align: right;"><b>FR-QAS-10-000</b><br><small>มีผลใช้งาน: 2026-05-08</small></div>
    </div>
    """, unsafe_allow_html=True)

# --- 4. ส่วนที่ 1 ---
st.subheader("ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ")
c1, c2 = st.columns(2)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
origin_main = c2.selectbox("ประเทศแหล่งปลูกหลัก *", ["ประเทศไทย", "จีน", "อื่นๆ"], key="origin_main")

# --- 5. ส่วนที่ 2 (ล็อกที่อยู่) ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

for i in range(st.session_state.items_count):
    with st.container():
        st.markdown(f'<div style="background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 15px;">', unsafe_allow_html=True)
        st.write(f"**รายการที่ {i+1}**")
        
        # ข้อมูลสินค้า
        r1, r2 = st.columns([3, 1])
        r1.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        r2.number_input("จำนวน (KG)", key=f"qty_{i}", min_value=0.0)

        # --- ส่วนที่อยู่ (Dropdown แบบบังคับค่าขึ้น) ---
        st.markdown("📍 **ที่อยู่แหล่งปลูก**")
        if origin_main == "ประเทศไทย" and not df_addr.empty:
            a1, a2, a3 = st.columns(3)
            
            # 1. จังหวัด
            p_list = sorted(df_addr["จังหวัด"].unique().tolist())
            p_val = a1.selectbox("จังหวัด", ["- เลือก -"] + p_list, key=f"p_{i}")
            
            # 2. อำเภอ (กรองตามจังหวัด)
            d_list = []
            if p_val != "- เลือก -":
                d_list = sorted(df_addr[df_addr["จังหวัด"] == p_val]["อำเภอ"].unique().tolist())
            a_val = a2.selectbox("อำเภอ", ["- เลือก -"] + d_list, key=f"a_{i}")
            
            # 3. ตำบล (กรองตามจังหวัดและอำเภอ)
            t_list = []
            if p_val != "- เลือก -" and a_val != "- เลือก -":
                t_list = sorted(df_addr[(df_addr["จังหวัด"] == p_val) & (df_addr["อำเภอ"] == a_val)]["ตำบล"].unique().tolist())
            t_val = a3.selectbox("ตำบล", ["- เลือก -"] + t_list, key=f"t_{i}")
            
        else:
            # ถ้าหาไฟล์ไม่เจอ หรือเลือกประเทศอื่น ให้กรอกเอง
            a1, a2, a3 = st.columns(3)
            a1.text_input("จังหวัด", key=f"p_man_{i}")
            a2.text_input("อำเภอ", key=f"a_man_{i}")
            a3.text_input("ตำบล", key=f"t_man_{i}")

        st.markdown('</div>', unsafe_allow_html=True)

if st.button("+ เพิ่มรายการ"):
    st.session_state.items_count += 1
    st.rerun()

# --- 6. สร้าง PDF ---
if st.button("📥 ดาวน์โหลด PDF", type="primary"):
    pdf = FPDF()
    pdf.add_page()
    # เรียกใช้ฟอนต์ใน GitHub
    if os.path.exists("Sarabun-Regular.ttf"):
        pdf.add_font('Sarabun', '', "Sarabun-Regular.ttf")
        pdf.set_font('Sarabun', '', 14)
        pdf.cell(0, 10, f"ผู้ส่งมอบ: {st.session_state.s_name}", ln=True)
        # แสดงรายการที่กรอก
        for i in range(st.session_state.items_count):
            pdf.cell(0, 10, f"{i+1}. {st.session_state.get(f'mat_{i}')} ({st.session_state.get(f'p_{i}')})", ln=True)
        
        st.download_button("คลิกเพื่อดาวน์โหลด", data=bytes(pdf.output()), file_name="form.pdf")
    else:
        st.error("ไม่พบไฟล์ฟอนต์ Sarabun-Regular.ttf")
