import os
import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import json

st.set_page_config(page_title="แบบบันข้อมูลประจำวันผู้ส่งมอบวัตถุดิบ", layout="wide")

# Excel file path for collecting submissions
EXCEL_PATH = os.path.expanduser("~/Desktop/vegetable_delivery_records.xlsx")

# Load Thailand provinces data
@st.cache_data
def load_thailand_data():
    try:
        df = pd.read_excel('thailand.xlsx', sheet_name=0)
        return df
    except Exception as e:
        st.warning(f"⚠️ ไม่สามารถโหลดข้อมูลจังหวัด: {str(e)}")
        return None

thailand_df = load_thailand_data()


def append_submission_to_excel(submission, excel_path):
    columns = [
        "อีเมล",
        "ผู้ส่งมอบวัตถุดิบ",
        "ที่อยู่ผู้ส่งมอบ",
        "วันที่ส่งมอบวัตถุดิบ",
        "จำนวนวัตถุดิบที่ส่ง",
        "ลำดับที่",
        "ชนิดวัตถุดิบที่ส่งมอบ",
        "Code",
        "จำนวน",
        "สายพันธุ์",
        "ลักษณะการปลูก",
        "ระบบการปลูก",
        "เวลาเก็บเกี่ยว",
        "วันที่ล้าง/ตัดแต่ง",
        "เวลาล้าง/ตัดแต่ง",
        "ชื่อผู้ปลูก",
        "เลขที่ GAP",
        "รหัสไร่",
        "จังหวัด",
        "อำเภอ",
        "ตำบล"
    ]

    rows = []
    for item in submission.get("raw_materials", []):
        rows.append({
            "อีเมล": submission.get("email", ""),
            "ผู้ส่งมอบวัตถุดิบ": submission.get("supplier_name", ""),
            "ที่อยู่ผู้ส่งมอบ": submission.get("supplier_address", ""),
            "วันที่ส่งมอบวัตถุดิบ": submission.get("delivery_date", ""),
            "จำนวนวัตถุดิบที่ส่ง": submission.get("quantity_count", ""),
            "ลำดับที่": item.get("ลำดับที่", ""),
            "ชนิดวัตถุดิบที่ส่งมอบ": item.get("ชนิดวัตถุดิบที่ส่งมอบ", ""),
            "Code": item.get("Code", ""),
            "จำนวน": item.get("จำนวน", ""),
            "สายพันธุ์": item.get("สายพันธุ์", ""),
            "ลักษณะการปลูก": item.get("ลักษณะการปลูก", ""),
            "ระบบการปลูก": item.get("ระบบการปลูก", ""),
            "เวลาเก็บเกี่ยว": item.get("เวลาเก็บเกี่ยว", ""),
            "วันที่ล้าง/ตัดแต่ง": item.get("วันที่ล้าง/ตัดแต่ง", ""),
            "เวลาล้าง/ตัดแต่ง": item.get("เวลาล้าง/ตัดแต่ง", ""),
            "ชื่อผู้ปลูก": item.get("ชื่อผู้ปลูก", ""),
            "เลขที่ GAP": item.get("เลขที่ GAP", ""),
            "รหัสไร่": item.get("รหัสไร่", ""),
            "จังหวัด": item.get("จังหวัด", ""),
            "อำเภอ": item.get("อำเภอ", ""),
            "ตำบล": item.get("ตำบล", "")
        })

    df = pd.DataFrame(rows, columns=columns)
    if os.path.exists(excel_path):
        existing = pd.read_excel(excel_path, engine='openpyxl')
        df = pd.concat([existing, df], ignore_index=True)
    df.to_excel(excel_path, index=False, engine='openpyxl')

# Style configuration
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #2c3e50;
        margin-bottom: 30px;
    }
    .section-header {
        background-color: #34495e;
        color: white;
        padding: 10px;
        border-radius: 4px;
        margin: 20px 0 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 class='main-header'>แบบบันข้อมูลประจำวันผู้ส่งมอบวัตถุดิบ</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='main-header'>กลุ่มผักสลัด</h3>", unsafe_allow_html=True)

from datetime import date, time, datetime
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

PDF_OUTPUT_DIR = os.path.expanduser("~/Desktop/vegetable_delivery_pdfs")
CREDENTIALS_PATH = os.path.expanduser("~/Desktop/vegetable_delivery_admin.json")
DEFAULT_ADMIN_CREDENTIALS = {"username": "admin", "password": "admin2026"}

# Logo search paths
LOGO_SEARCH_PATHS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "cpram_logo.png"),
    os.path.join(os.path.expanduser("~"), "Desktop", "cpram_logo.png"),
    os.path.join(os.path.expanduser("~"), "Desktop", "cpram_logo.jpg"),
    os.path.join(os.path.expanduser("~"), "Desktop", "cpram_logo.jpeg"),
]


def load_admin_credentials():
    if os.path.exists(CREDENTIALS_PATH):
        try:
            with open(CREDENTIALS_PATH, 'r', encoding='utf-8') as f:
                creds = json.load(f)
                if creds.get('username') and creds.get('password'):
                    return creds
        except Exception:
            pass
    save_admin_credentials(DEFAULT_ADMIN_CREDENTIALS)
    return DEFAULT_ADMIN_CREDENTIALS.copy()


def save_admin_credentials(creds):
    os.makedirs(os.path.dirname(CREDENTIALS_PATH), exist_ok=True)
    with open(CREDENTIALS_PATH, 'w', encoding='utf-8') as f:
        json.dump(creds, f, ensure_ascii=False, indent=2)
    return creds

# Initialize session state
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}
if 'last_pdf_bytes' not in st.session_state:
    st.session_state.last_pdf_bytes = None
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False
if 'admin_credentials' not in st.session_state:
    st.session_state.admin_credentials = load_admin_credentials()


def get_preferred_thai_font():
    font_name = 'THSarabunPSK'
    if font_name not in pdfmetrics.getRegisteredFontNames():
        font_candidates = [
            '/Library/Fonts/TH Sarabun PSK.ttf',
            '/Library/Fonts/THSarabunNew.ttf',
            '/Library/Fonts/Arial Unicode.ttf',
            '/Library/Fonts/Arial Unicode MS.ttf',
            '/System/Library/Fonts/Arial Unicode.ttf',
            '/System/Library/Fonts/Arial.ttf'
        ]
        for font_path in font_candidates:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    return font_name
                except Exception:
                    continue
        return 'Helvetica'
    return font_name


def save_pdf_to_disk(pdf_bytes, filename):
    os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
    path = os.path.join(PDF_OUTPUT_DIR, filename)
    with open(path, 'wb') as f:
        f.write(pdf_bytes)
    return path


def find_logo_path():
    for path in LOGO_SEARCH_PATHS:
        if os.path.exists(path):
            return path
    return None


def build_pdf_bytes(form_data):
    """
    Build PDF by overlaying form data on template using TH SarabunPSK font size 16.
    """
    template_path = "/Users/natchatho/Documents/CP/แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด.pdf"
    
    if not os.path.exists(template_path):
        return create_canvas_pdf(form_data)
    
    try:
        from PyPDF2 import PdfReader, PdfWriter
        
        # Load template
        with open(template_path, 'rb') as f:
            reader = PdfReader(f)
            template_page = reader.pages[0]
        
        page_width = float(template_page.mediabox.width)
        page_height = float(template_page.mediabox.height)
        
        # Create overlay canvas
        overlay_buffer = BytesIO()
        overlay_canvas = canvas.Canvas(overlay_buffer, pagesize=(page_width, page_height))
        
        thai_font = get_preferred_thai_font()
        overlay_canvas.setFont(thai_font, 16)
        
        # Form field positions (adjusted for A4 template)
        # X coordinates for different columns
        col1_x = 60
        col2_x = 320
        col3_x = 500
        
        # Y position (start from top, decrease as we go down)
        y = page_height - 80
        line_height = 22
        
        # Row 1: Email and Supplier name
        email = form_data.get("email", "")[:50]
        supplier_name = form_data.get("supplier_name", "")[:40]
        overlay_canvas.drawString(col1_x + 80, y, email)
        overlay_canvas.drawString(col2_x + 80, y, supplier_name)
        y -= line_height
        
        # Row 2: Supplier contact and Date
        supplier_contact = form_data.get("supplier_contact", "")[:30]
        delivery_date = str(form_data.get("delivery_date", ""))[:10]
        overlay_canvas.drawString(col1_x + 80, y, supplier_contact)
        overlay_canvas.drawString(col2_x + 80, y, delivery_date)
        y -= line_height
        
        # Row 3: Address (can span multiple lines)
        address = f"{form_data.get('address', '')} {form_data.get('subdistrict', '')} {form_data.get('district', '')} {form_data.get('province', '')}"
        address = address.strip()[:80]
        overlay_canvas.drawString(col1_x + 80, y, address)
        y -= line_height * 2
        
        # Raw materials section
        materials = form_data.get("raw_materials", [])
        for i, material in enumerate(materials, 1):
            if y < 150:  # New page if needed
                overlay_canvas.save()
                overlay_buffer.seek(0)
                overlay_reader = PdfReader(overlay_buffer)
                overlay_page = overlay_reader.pages[0]
                template_page.merge_page(overlay_page)
                
                overlay_buffer = BytesIO()
                overlay_canvas = canvas.Canvas(overlay_buffer, pagesize=(page_width, page_height))
                overlay_canvas.setFont(thai_font, 16)
                y = page_height - 80
            
            if isinstance(material, dict):
                material_type = material.get("ชนิดวัตถุดิบที่ส่งมอบ", "")[:30]
                code = material.get("Code", "")[:15]
                qty = str(material.get("จำนวน", ""))[:10]
                variety = material.get("สายพันธุ์", "")[:25]
                
                # Material header
                overlay_canvas.setFont(thai_font, 14)
                overlay_canvas.drawString(col1_x, y, f"วัตถุดิบที่ {i}")
                overlay_canvas.setFont(thai_font, 16)
                y -= line_height
                
                # Row 1: Type, Code, Quantity, Variety
                overlay_canvas.drawString(col1_x + 30, y, material_type)
                overlay_canvas.drawString(col2_x + 30, y, code)
                overlay_canvas.drawString(col3_x, y, qty)
                y -= line_height
                
                # Row 2: Planting and System
                planting = material.get("ลักษณะการปลูก", "")[:25]
                system = material.get("ระบบการปลูก", "")[:25]
                overlay_canvas.drawString(col1_x + 30, y, planting)
                overlay_canvas.drawString(col2_x + 30, y, system)
                y -= line_height
                
                # Row 3: Dates
                harvest_date = material.get("วันที่เก็บเกี่ยว", "")[:10]
                wash_date = material.get("วันที่ล้าง/ตัดแต่ง", "")[:10]
                overlay_canvas.drawString(col1_x + 30, y, harvest_date)
                overlay_canvas.drawString(col2_x + 30, y, wash_date)
                y -= line_height
                
                # Row 4: Grower info
                grower = material.get("ชื่อผู้ปลูก", "")[:35]
                gap = material.get("เลขที่ GAP", "")[:20]
                overlay_canvas.drawString(col1_x + 30, y, grower)
                overlay_canvas.drawString(col2_x + 30, y, gap)
                y -= line_height
                
                # Row 5: Location
                location = f"{material.get('จังหวัด', '')} {material.get('อำเภอ', '')} {material.get('ตำบล', '')}"
                location = location.strip()[:60]
                overlay_canvas.drawString(col1_x + 30, y, location)
                y -= line_height * 2
        
        overlay_canvas.save()
        overlay_buffer.seek(0)
        
        # Merge overlay with template
        overlay_reader = PdfReader(overlay_buffer)
        overlay_page = overlay_reader.pages[0]
        template_page.merge_page(overlay_page)
        
        # Write final PDF
        output_buffer = BytesIO()
        writer = PdfWriter()
        writer.add_page(template_page)
        writer.write(output_buffer)
        output_buffer.seek(0)
        
        return output_buffer.getvalue()
        
    except Exception as e:
        return create_canvas_pdf(form_data)


def create_canvas_pdf(form_data):
    """Fallback canvas-based PDF generation when template is not available."""
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    left_margin = 40
    right_margin = 40
    font_name = get_preferred_thai_font()
    line_height = 16

    def draw_text(text, x, y, size=11):
        c.setFont(font_name, size)
        c.drawString(x, y, text)

    def draw_line(x, y, length):
        c.line(x, y, x + length, y)

    def draw_field(label, value, x, y, label_width=100, line_width=80):
        draw_text(label, x, y, size=10)
        draw_line(x + label_width, y - 4, line_width)
        if value:
            draw_text(str(value), x + label_width + 5, y, size=10)

    # Draw logo at top right
    logo_path = find_logo_path()
    if logo_path:
        try:
            logo_width = 80
            logo_height = 24
            logo_x = width - right_margin - logo_width
            logo_y = height - 45
            c.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height, 
                       preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # Title
    y = height - 50
    draw_text("แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด", left_margin, y, size=13)
    y -= 18

    # Section: ข้อมูลเบื้องต้น
    draw_text("ข้อมูลเบื้องต้น", left_margin, y, size=12)
    y -= 16

    # Email and Supplier name
    draw_field("อีเมล:", form_data.get("email", ""), left_margin, y, label_width=70, line_width=100)
    draw_field("ผู้ส่งมอบ:", form_data.get("supplier_name", ""), 320, y, label_width=70, line_width=220)
    y -= line_height

    # Delivery date and Quantity
    draw_field("วันที่ส่ง:", form_data.get("delivery_date", ""), left_margin, y, label_width=70, line_width=100)
    qty_val = form_data.get("quantity_count", "")
    if qty_val and qty_val != "-- เลือกจำนวน --":
        qty_val = str(qty_val)
    else:
        qty_val = ""
    draw_field("จำนวน:", qty_val, 320, y, label_width=70, line_width=80)
    y -= line_height

    # Address
    draw_text("ที่อยู่ผู้ส่งมอบ:", left_margin, y, size=10)
    y -= 12
    address = f"{form_data.get('supplier_address', '')}, {form_data.get('address', '')}"
    draw_text(address, left_margin + 20, y, size=10)
    y -= line_height * 2

    # Raw materials
    if y < 180:
        c.showPage()
        y = height - 50

    draw_text("ข้อมูลวัตถุดิบส่งมอบ", left_margin, y, size=12)
    y -= 16

    for idx, item in enumerate(form_data.get("raw_materials", []), start=1):
        if y < 140:
            c.showPage()
            y = height - 50

        material_type = item.get('ชนิดวัตถุดิบที่ส่งมอบ', '')
        draw_text(f"• วัตถุดิบที่ {idx}: {material_type}", left_margin, y, size=11)
        y -= 14

        draw_field("Code:", item.get("Code", ""), left_margin, y, label_width=50, line_width=50)
        draw_field("จำนวน:", item.get("จำนวน", ""), 220, y, label_width=50, line_width=50)
        draw_field("สายพันธุ์:", item.get("สายพันธุ์", ""), 420, y, label_width=60, line_width=120)
        y -= line_height

        draw_field("ปลูก:", item.get("ลักษณะการปลูก", ""), left_margin, y, label_width=50, line_width=80)
        draw_field("ระบบ:", item.get("ระบบการปลูก", ""), 280, y, label_width=50, line_width=100)
        y -= line_height

        y -= 16

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


def validate_submission(form_data):
    errors = []
    if not form_data['email']:
        errors.append("กรุณากรอกอีเมล")
    if not form_data['supplier_name']:
        errors.append("กรุณากรอกผู้ส่งมอบ")
    if not form_data['supplier_address']:
        errors.append("กรุณากรอกที่อยู่ผู้ส่งมอบ")
    if not form_data['delivery_date']:
        errors.append("กรุณาเลือกวันที่ส่งมอบ")
    if form_data['quantity_count'] == "-- เลือกจำนวน --":
        errors.append("กรุณาเลือกจำนวนวัตถุดิบที่ส่ง")

    for idx, material in enumerate(form_data['raw_materials'], 1):
        if not material.get("ชนิดวัตถุดิบที่ส่งมอบ"):
            errors.append(f"วัตถุดิบที่ {idx}: กรุณากรอกชนิดวัตถุดิบ")
        if not material.get("จำนวน"):
            errors.append(f"วัตถุดิบที่ {idx}: กรุณากรอกจำนวน")
        if not material.get("สายพันธุ์"):
            errors.append(f"วัตถุดิบที่ {idx}: กรุณากรอกสายพันธุ์")
        if not material.get("ลักษณะการปลูก"):
            errors.append(f"วัตถุดิบที่ {idx}: กรุณาเลือกลักษณะการปลูก")
        if not material.get("ระบบการปลูก"):
            errors.append(f"วัตถุดิบที่ {idx}: กรุณากรอกระบบการปลูก")
        if not material.get("ชื่อผู้ปลูก"):
            errors.append(f"วัตถุดิบที่ {idx}: กรุณากรอกชื่อผู้ปลูก")
    return errors


def render_submission_form():
    st.markdown("<div class='section-header'>ข้อมูลเบื้องต้น</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input("อีเมล *", key="email")
    with col2:
        supplier_name = st.text_input("ผู้ส่งมอบวัตถุดิบ *", key="supplier_name")

    supplier_address = st.text_area("ที่อยู่ผู้ส่งมอบ *", key="supplier_address")

    col3, col4 = st.columns(2)
    with col3:
        delivery_date = st.date_input("วันที่ส่งมอบวัตถุดิบ *", key="delivery_date")
    with col4:
        quantity_count = st.selectbox(
            "จำนวนวัตถุดิบที่ส่ง *",
            options=["-- เลือกจำนวน --", 1, 2, 3, 4, 5],
            key="quantity_count"
        )

    st.markdown("<div class='section-header'>ข้อมูลวัตถุดิบส่งมอบ</div>", unsafe_allow_html=True)
    st.info("📋 กรุณากรอกรายละเอียดสำหรับแต่ละชุดของวัตถุดิบที่ส่งมอบ")

    raw_materials_data = []
    if quantity_count != "-- เลือกจำนวน --":
        quantity_count = int(quantity_count)
        for i in range(1, quantity_count + 1):
            with st.expander(f"วัตถุดิบที่ {i}", expanded=(i == 1)):
                col1, col2 = st.columns(2)
                with col1:
                    material_type = st.text_input("ชนิดวัตถุดิบที่ส่งมอบ *", key=f"material_type_{i}")
                with col2:
                    code = st.text_input("Code", key=f"code_{i}")

                col3, col4 = st.columns(2)
                with col3:
                    qty = st.number_input("จำนวน *", min_value=0.0, step=0.01, key=f"qty_{i}")
                with col4:
                    variety = st.text_input("สายพันธุ์ *", key=f"variety_{i}")

                st.write("**ลักษณะการปลูก** *")
                planting_method = st.radio(
                    "เลือกลักษณะการปลูก",
                    ["ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ไฮโดรโปนิกส์"],
                    key=f"method_{i}",
                    label_visibility="collapsed"
                )

                st.write("**ระบบการปลูก** *")
                planting_system = st.radio(
                    "เลือกระบบการปลูก",
                    ["ระบบเปิด", "ระบบปิด"],
                    key=f"system_{i}",
                    label_visibility="collapsed"
                )

                col5, col6 = st.columns(2)
                with col5:
                    harvest_date = st.date_input("วันที่เก็บเกี่ยว", key=f"harvest_date_{i}")
                with col6:
                    harvest_time = st.time_input("เวลาเก็บเกี่ยว", key=f"harvest_time_{i}")

                col7, col8 = st.columns(2)
                with col7:
                    wash_date = st.date_input("วันที่ล้าง/ตัดแต่ง", key=f"wash_date_{i}")
                with col8:
                    wash_time = st.time_input("เวลาล้าง/ตัดแต่ง", key=f"wash_time_{i}")

                col9, col10 = st.columns(2)
                with col9:
                    grower_name = st.text_input("ชื่อผู้ปลูก *", key=f"grower_name_{i}")
                with col10:
                    gap_number = st.text_input("เลขที่ GAP", key=f"gap_number_{i}")

                farm_code = st.text_input("รหัสไร่", key=f"farm_code_{i}")

                st.write("**ที่ตั้งไร่ (จังหวัด/อำเภอ/ตำบล)** *")
                col11, col12, col13 = st.columns(3)
                if thailand_df is not None:
                    provinces = sorted(thailand_df["จังหวัด"].unique().tolist())
                else:
                    provinces = []

                with col11:
                    province = st.selectbox("จังหวัด", ["-- เลือกจังหวัด --"] + provinces, key=f"province_{i}")

                districts = ["-- เลือกอำเภอ --"]
                if thailand_df is not None and province != "-- เลือกจังหวัด --":
                    districts = sorted(thailand_df[thailand_df["จังหวัด"] == province]["อำเภอ"].unique().tolist())
                    districts = ["-- เลือกอำเภอ --"] + districts

                with col12:
                    district = st.selectbox("อำเภอ", districts, key=f"district_{i}")

                sub_districts = ["-- เลือกตำบล --"]
                if thailand_df is not None and province != "-- เลือกจังหวัด --" and district != "-- เลือกอำเภอ --":
                    sub_districts = sorted(thailand_df[(thailand_df["จังหวัด"] == province) &
                                                       (thailand_df["อำเภอ"] == district)]["ตำบล"].unique().tolist())
                    sub_districts = ["-- เลือกตำบล --"] + sub_districts

                with col13:
                    sub_district = st.selectbox("ตำบล", sub_districts, key=f"sub_district_{i}")

                clean_province = province if province and not province.startswith("--") else ""
                clean_district = district if district and not district.startswith("--") else ""
                clean_sub_district = sub_district if sub_district and not sub_district.startswith("--") else ""

                raw_materials_data.append({
                    "ลำดับที่": i,
                    "ชนิดวัตถุดิบที่ส่งมอบ": material_type,
                    "Code": code,
                    "จำนวน": qty,
                    "สายพันธุ์": variety,
                    "ลักษณะการปลูก": planting_method,
                    "ระบบการปลูก": planting_system,
                    "วันที่เก็บเกี่ยว": str(harvest_date),
                    "เวลาเก็บเกี่ยว": str(harvest_time),
                    "วันที่ล้าง/ตัดแต่ง": str(wash_date),
                    "เวลาล้าง/ตัดแต่ง": str(wash_time),
                    "ชื่อผู้ปลูก": grower_name,
                    "เลขที่ GAP": gap_number,
                    "รหัสไร่": farm_code,
                    "จังหวัด": clean_province,
                    "อำเภอ": clean_district,
                    "ตำบล": clean_sub_district
                })

    return {
        "email": email,
        "supplier_name": supplier_name,
        "supplier_address": supplier_address,
        "delivery_date": str(delivery_date),
        "quantity_count": quantity_count,
        "raw_materials": raw_materials_data
    }


def load_all_submissions(excel_path):
    if os.path.exists(excel_path):
        try:
            return pd.read_excel(excel_path, engine='openpyxl')
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


# Sidebar: Mode selector
st.sidebar.markdown("---")
mode = st.sidebar.radio("เลือกโหมด", ["👤 ผู้ส่งข้อมูล", "🔐 ผู้สร้าง"])

# Admin authentication for creator mode
if mode == "🔐 ผู้สร้าง":
    st.sidebar.subheader("เข้าสู่ระบบผู้สร้าง")
    username = st.sidebar.text_input("ชื่อผู้ใช้", key="creator_username")
    password = st.sidebar.text_input("รหัสผ่าน", type="password", key="creator_password")
    if st.sidebar.button("เข้าสู่ระบบ"):
        creds = st.session_state.admin_credentials
        if username == creds.get("username") and password == creds.get("password"):
            st.session_state.admin_authenticated = True
            st.sidebar.success("✅ เข้าสู่ระบบสำเร็จ")
        else:
            st.session_state.admin_authenticated = False
            st.sidebar.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    
    if st.session_state.admin_authenticated:
        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ จัดการรหัสผ่าน")
        new_username = st.sidebar.text_input("ชื่อผู้ใช้ใหม่", value=st.session_state.admin_credentials.get("username", ""))
        new_password = st.sidebar.text_input("รหัสผ่านใหม่", type="password")
        confirm_password = st.sidebar.text_input("ยืนยันรหัสผ่าน", type="password")
        if st.sidebar.button("บันทึกการตั้งค่า"):
            if new_username.strip() and new_password and new_password == confirm_password:
                st.session_state.admin_credentials = save_admin_credentials({"username": new_username, "password": new_password})
                st.sidebar.success("✅ บันทึกเรียบร้อย")
            else:
                st.sidebar.error("❌ ตรวจสอบข้อมูล")
else:
    st.sidebar.info("📝 โหมดผู้ส่งข้อมูล")

# Show form only in supplier mode or when authenticated as creator
if mode == "👤 ผู้ส่งข้อมูล" or st.session_state.admin_authenticated:
    form_data = render_submission_form()
    
    if form_data["quantity_count"] != "-- เลือกจำนวน --":
        current_quantity = int(form_data["quantity_count"])
    else:
        current_quantity = 0

    submit_button_label = "ส่งข้อมูลและดาวน์โหลด PDF"
    if st.button(submit_button_label, use_container_width=True):
        errors = validate_submission(form_data)
        if errors:
            st.error("❌ กรุณาแก้ไขข้อผิดพลาดต่อไปนี้:\n" + "\n".join(errors))
        else:
            append_submission_to_excel(form_data, EXCEL_PATH)
            pdf_bytes = build_pdf_bytes(form_data)
            st.session_state.last_pdf_bytes = pdf_bytes
            saved_path = save_pdf_to_disk(pdf_bytes, f"vegetable_delivery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            st.success(f"✅ บันทึกข้อมูลและสร้าง PDF เรียบร้อยแล้ว ({saved_path})")

    if st.session_state.last_pdf_bytes is not None:
        st.download_button(
            label="⬇️ ดาวน์โหลด PDF แบบฟอร์ม",
            data=st.session_state.last_pdf_bytes,
            file_name=f"vegetable_delivery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )
    
    # Show submissions in creator mode
    if st.session_state.admin_authenticated:
        st.markdown("---")
        st.subheader("📁 ข้อมูลที่บันทึก")
        submissions_df = load_all_submissions(EXCEL_PATH)
        if not submissions_df.empty:
            st.dataframe(submissions_df, use_container_width=True)
        else:
            st.info("ยังไม่มีข้อมูลจัดเก็บ")
else:
    st.warning("🔐 กรุณาเข้าสู่ระบบเพื่อใช้งาน")
