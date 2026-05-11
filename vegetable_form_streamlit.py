# --- 6. ส่วนที่ 2 — รายการวัตถุดิบ (ปรับปรุง UI ตามรูป) ---
st.markdown('<div class="section-header">ส่วนที่ 2 — รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด)</div>', unsafe_allow_html=True)

for i in range(st.session_state.items_count):
    # ใช้ container และสไตล์ item-box ที่คุณตั้งไว้
    st.markdown(f'<div class="item-box">', unsafe_allow_html=True)
    
    # หัวข้อรายการและปุ่มลบ (ถ้ามีรายการเดียวจะไม่แสดงปุ่มลบเพื่อความสวยงาม)
    header_col, delete_col = st.columns([0.8, 0.2])
    header_col.subheader(f"รายการที่ {i+1}")
    if st.session_state.items_count > 1:
        if delete_col.button(f"❌ ลบรายการที่ {i+1}", key=f"del_btn_{i}"):
            # ใช้เทคนิคข้ามรายการนี้ในการประมวลผลหรือลด count (ในที่นี้แนะนำปุ่มลบล่างสุดจะเสถียรสุด)
            pass

    # --- แถวที่ 1: ข้อมูลพื้นฐาน ---
    r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
    r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
    r1c2.text_input("Code", placeholder="เช่น 71000277", key=f"code_{i}")
    r1c3.number_input("จำนวน (KG) *", min_value=0.0, step=0.1, key=f"qty_{i}")

    # --- แถวที่ 2: วันเวลาเก็บเกี่ยวและล้าง ---
    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    r2c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
    r2c2.text_input("เวลาเก็บเกี่ยว", placeholder="เช่น 08:00", key=f"ht_{i}")
    r2c3.date_input("วันที่ล้างทำความสะอาด", key=f"cd_{i}")
    r2c4.text_input("เวลาที่ล้างทำความสะอาด", placeholder="เช่น 08:00 หรือ 08:00-09:30", key=f"ct_{i}")

    # --- แถวที่ 3: ข้อมูลผู้ปลูกและรหัสไร่ ---
    r3c1, r3c2, r3c3, r3c4 = st.columns(4)
    r3c1.text_input("ชื่อผู้ปลูก", key=f"grower_{i}")
    r3c2.text_input("เลขที่ GAP", key=f"gap_{i}")
    r3c3.text_input("รหัสไร่", key=f"farm_{i}")
    r3c4.text_input("ที่อยู่เลขที่", placeholder="บ้านเลขที่/หมู่ที่", key=f"addr_no_{i}")

    # --- แถวที่ 4: Cascading Dropdown (ที่อยู่แหล่งปลูก) ---
    st.markdown("📍 **ที่อยู่แหล่งปลูก (Cascading Dropdown)**")
    r4c1, r4c2, r4c3, r4c4 = st.columns(4)
    
    zip_code = ""
    if not df_addr.empty:
        # ใช้ชื่อคอลัมน์ให้ตรงกับไฟล์ thailand.xlsx (ในรูปคุณคือ นนทบุรี, ปากเกร็ด)
        p_col = 'province_th'
        a_col = 'district_th'
        t_col = 'subdistrict_th'
        z_col = 'postcode'

        province_list = sorted(df_addr[p_col].unique())
        sel_prov = r4c1.selectbox("จังหวัด/มณฑล", ["- เลือก -"] + province_list, key=f"prov_{i}")
        
        amp_list = ["- เลือกจังหวัดก่อน -"]
        if sel_prov != "- เลือก -":
            amp_list = sorted(df_addr[df_addr[p_col] == sel_prov][a_col].unique())
        sel_amp = r4c2.selectbox("อำเภอ/เมือง", ["- เลือก -"] + amp_list, key=f"amp_{i}")
        
        tam_list = ["- เลือกอำเภอก่อน -"]
        if sel_amp != "- เลือก -":
            tam_list = sorted(df_addr[(df_addr[p_col] == sel_prov) & (df_addr[a_col] == sel_amp)][t_col].unique())
        sel_tam = r4c3.selectbox("ตำบล/เขต", ["- เลือก -"] + tam_list, key=f"tam_{i}")
        
        if sel_tam != "- เลือก -":
            res = df_addr[(df_addr[p_col] == sel_prov) & (df_addr[a_col] == sel_amp) & (df_addr[t_col] == sel_tam)]
            if not res.empty:
                zip_code = res[z_col].iloc[0]
    
    r4c4.text_input("รหัสไปรษณีย์", value=str(zip_code), key=f"zip_display_{i}", disabled=True)

    # --- แถวที่ 5: ข้อมูลสายพันธุ์และลักษณะการปลูก ---
    r5c1, r5c2, r5c3 = st.columns(3)
    r5c1.text_input("สายพันธุ์", key=f"breed_{i}")
    r5c2.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
    r5c3.selectbox("ลักษณะสถานที่ปลูก", ["- เลือก -", "โรงเรือน", "แปลงเปิด"], key=f"loc_type_{i}")

    st.markdown('</div>', unsafe_allow_html=True)
