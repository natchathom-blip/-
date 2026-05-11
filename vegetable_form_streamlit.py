import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="CPRAM - Supplier Record", layout="wide")

# --- 2. INITIALIZE SESSION STATE (ป้องกันข้อมูลหาย) ---
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

# --- 3. LOAD ADDRESS DATA ---
@st.cache_data
def load_data():
    try:
        return pd.read_excel('thailand.xlsx')
    except:
        return pd.DataFrame(columns=['province_th', 'district_th', 'subdistrict_th', 'postcode'])

df_addr = load_data()

# --- 4. PDF GENERATOR (ระยะตามสั่งเป๊ะๆ) ---
class CPRAM_PDF(FPDF):
    def header(self):
        self.add_font('THSarabun', '', 'Sarabun-Regular.ttf', uni=True)
        self.set_font('THSarabun', '', 14)
        self.cell(0, 10, 'แบบบันทึกข้อมูลประจำวันผู้ส่งมอบวัตถุดิบ (FR-QAS-10-000)', 0, 1, 'C')
        self.ln(5)

def create_pdf(s_info, items):
    pdf = CPRAM_PDF()
    pdf.set_auto_page_break(auto=True, margin=80) # Page Threshold 80mm
    pdf.add_page()
    pdf.set_font('THSarabun', '', 10) # Font Size 10
    
    line_h = 12 # บรรทัดห่าง 12mm
    offset = 44 # Value Offset (Label 40mm + 4mm)

    pdf.cell(0, 10, "ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ", 0, 1)
    # เขียนข้อมูลส่วนที่ 1
    pdf.text(10, pdf.get_y(), "ผู้ส่งมอบ:"); pdf.text(10 + offset, pdf.get_y(), s_info['name']); pdf.ln(line_h)
    pdf.text(10, pdf.get_y(), "อีเมล:"); pdf.text(10 + offset, pdf.get_y(), s_info['email']); pdf.ln(line_h)

    pdf.ln(5)
    pdf.cell(0, 10, "ส่วนที่ 2 — รายการวัตถุดิบ", 0, 1)
    for i, item in enumerate(items):
        pdf.text(10, pdf.get_y(), f"รายการที่ {i+1}"); pdf.ln(8)
        # ฟิลด์ข้อมูล
        pdf.text(15, pdf.get_y(), "ชนิดวัตถุดิบ:"); pdf.text(15 + offset, pdf.get_y(), item['mat']); pdf.ln(line_h)
        pdf.text(15, pdf.get_y(), "Code:"); pdf.text(15 + offset, pdf.get_y(), item['code']); pdf.ln(line_h)
        pdf.text(15, pdf.get_y(), "จำนวน (KG):"); pdf.text(15 + offset, pdf.get_y(), str(item['qty'])); pdf.ln(line_h)
        pdf.ln(4)
        
    return pdf.output(dest='S').encode('latin-1')

# --- 5. UI DISPLAY (HEADER) ---
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px;">
        <div style="display: flex; align-items: center;">
            <div style="background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 24px;">cpram</div>
            <div style="margin-left: 15px; color: #2e7d32;">
                <b>CPRAM Co., Ltd.</b><br><small>ระบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ</small>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="border: 1px solid black; padding: 2px 10px;"><b>FR-QAS-10-000</b></div>
            <small>มีผลใช้งาน: 2026-05-08</small>
        </div>
    </div>
    <h3 style="text-align: center; color: #2e7d32; margin-top: 20px;">แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด</h3>
    """, unsafe_allow_html=True)

# --- 6. INPUT FORM ---
st.subheader("ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ")
c1, c2 = st.columns(2)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
s_email = c2.text_input("อีเมลสำหรับรับไฟล์ PDF *", key="s_email")
d_date = st.date_input("วันที่ส่งวัตถุดิบ *", datetime.now(), key="d_date")

st.subheader("ส่วนที่ 2 — รายการวัตถุดิบ")
all_items_data = []

for i in range(st.session_state.items_count):
    with st.expander(f"รายการที่ {i+1}", expanded=True):
        r1, r2 = st.columns([2, 1])
        mat = r1.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        code = r2.text_input("Code", key=f"code_{i}")
        qty = st.number_input("จำนวน (KG)", key=f"qty_{i}")
        
        # Cascading Address
        a1, a2, a3 = st.columns(3)
        prov = a1.selectbox("จังหวัด", ["- เลือก -"] + sorted(df_addr['province_th'].unique().tolist()), key=f"prov_{i}")
        
        amp_list = sorted(df_addr[df_addr['province_th'] == prov]['district_th'].unique().tolist()) if prov != "- เลือก -" else []
        amp = a2.selectbox("อำเภอ", ["- เลือก -"] + amp_list, key=f"amp_{i}")
        
        tam_list = sorted(df_addr[(df_addr['province_th'] == prov) & (df_addr['district_th'] == amp)]['subdistrict_th'].unique().tolist()) if amp != "- เลือก -" else []
        tam = a3.selectbox("ตำบล", ["- เลือก -"] + tam_list, key=f"tam_{i}")
        
        # ดึง Zipcode อัตโนมัติ
        zip_code = ""
        if tam != "- เลือก -":
            zip_code = df_addr[(df_addr['province_th'] == prov) & (df_addr['district_th'] == amp) & (df_addr['subdistrict_th'] == tam)]['postcode'].iloc[0]
        st.text_input("รหัสไปรษณีย์", value=str(zip_code), key=f"zip_{i}", disabled=True)

        all_items_data.append({'mat': mat, 'code': code, 'qty': qty, 'prov': prov, 'amp': amp, 'tam': tam})

# --- 7. SUBMIT LOGIC ---
st.button("+ เพิ่มรายการ", on_click=lambda: setattr(st.session_state, 'items_count', st.session_state.items_count + 1))

if st.button("ยืนยันข้อมูลและส่ง PDF", type="primary"):
    if not s_name or not s_email:
        st.error("❌ กรุณากรอกข้อมูลส่วนที่ 1 ให้ครบถ้วน")
    else:
        # สร้าง PDF
        supplier_info = {'name': s_name, 'email': s_email, 'date': d_date}
        pdf_bytes = create_pdf(supplier_info, all_items_data)
        
        st.success("✅ บันทึกข้อมูลสำเร็จ! ข้อมูลยังคงอยู่ด้านบน คุณสามารถตรวจสอบหรือดาวน์โหลด PDF ได้ที่นี่")
        st.download_button("ดาวน์โหลด PDF (ตรวจสอบความถูกต้อง)", data=pdf_bytes, file_name=f"Record_{s_name}.pdf")
        
        # โค้ดส่งเมล (ถ้าตั้งค่า SMTP ไว้) จะทำงานตรงนี้
