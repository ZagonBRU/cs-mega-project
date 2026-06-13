import streamlit as st
import pandas as pd
import json
import os

PASSWORD = "CS69"

PROJECT_FILE = "Project_List.json"
ITEM_FILE = "Item_List.json"
TEAM_FILE = "Team_List.json"
DATA_FILE = "Data.json"

def load_json(file_name, default_value):
    if not os.path.exists(file_name):
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(default_value, f, ensure_ascii=False, indent=4)
        return default_value
    with open(file_name, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file_name, data):
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# โหลดฐานข้อมูลทั้งหมดเข้าสู่ระบบคุมเกม
TEAMS = load_json(TEAM_FILE, ["แดง 1", "แดง 2", "เหลือง 1", "เหลือง 2", "เขียว 1", "เขียว 2", "ฟ้า 1", "ฟ้า 2"])
MATERIAL_PRICES = load_json(ITEM_FILE, {"ไม้เสียบลูกชิ้น *": 2000, "ตะเกียบ *": 4000, "กระดาษ A4": 2000})
PROJECT_MASTER = load_json(PROJECT_FILE, {})
GAME_DATA = load_json(DATA_FILE, [])

# 🛠️ ฟังก์ชันตรรกะสากลสำหรับเจนเนอเรตคำห้อยท้ายสถานะโปรเจ็คใน Dropdown ทุกจุดอัตโนมัติ
def get_deal_status_label(deal):
    res = deal.get("result", "รอตรวจ")
    times = deal.get("times", 0)
    shop_received = deal.get("shop_received", False)
    
    if res == "ผ่าน":
        return " (สำเร็จ)"
    elif res == "ยกเลิก":
        return " (ยกเลิก)"
    elif res == "ไม่ผ่าน":
        return f" (กำลังดำเนินการ: ตรวจแล้ว #{times})"
    else: # กรณีสถานะ "รอตรวจ" (ดีลงานที่เพิ่งคีย์สัญญากดลงทะเบียนเข้ามาใหม่)
        if not shop_received:
            return " (กำลังดำเนินการ: รอรับของ)"
        else:
            return " (กำลังดำเนินการ: รับของแล้ว)"

# ประมวลผลหา "สถานะปัจจุบัน" ของโปรเจ็คแต่ละระดับความยากแบบ Dynamic (สำหรับการคุมกติกาหลังบ้าน)
STATUS_MAP = {}
for deal in GAME_DATA:
    key = f"{deal['project_id']}-{deal['difficulty']}"
    if deal["result"] == "ผ่าน":
        STATUS_MAP[key] = "เสร็จสิ้น"
    elif deal["result"] == "รอตรวจ" and STATUS_MAP.get(key) != "เสร็จสิ้น":
        STATUS_MAP[key] = "กำลังดำเนินการ"
    elif deal["result"] == "ไม่ผ่าน" and STATUS_MAP.get(key) not in ["กำลังดำเนินการ", "เสร็จสิ้น"]:
        STATUS_MAP[key] = "กำลังดำเนินการ"
    elif deal["result"] == "ยกเลิก" and STATUS_MAP.get(key) not in ["กำลังดำเนินการ", "เสร็จสิ้น"]:
        STATUS_MAP[key] = "ว่าง"

# 🧭 เมนูแท็บการจัดหน้าสตรีมลิต
tab1, tab2, tab4, tab3 = st.tabs([
    "🌐 คู่มือและบอร์ดสถานะโปรเจ็ค (สำหรับนักศึกษา)", 
    "🔐 ระบบควบคุมเกม (Staff Only)", 
    "🏪 ระบบสำหรับร้านค้าเบิกจ่ายวัสดุ (Shop Only)",
    "🏆 สรุปคะแนนลีดเดอร์บอร์ด (Staff Only)"
])

# ฟังก์ชันกลางสำหรับตรวจสอบการล็อกอินรหัสผ่าน CS69 เพื่อป้องกันโค้ดซ้ำซ้อน
def check_staff_authentication(tab_object, session_key_name):
    if session_key_name not in st.session_state:
        st.session_state[session_key_name] = False
        
    if not st.session_state[session_key_name]:
        with tab_object:
            st.warning("🔒 เนื้อหาส่วนนี้จำกัดสิทธิ์เฉพาะอาจารย์และเจ้าหน้าที่ควบคุมระบบเท่านั้น")
            pwd = st.text_input("กรอกรหัสผ่านเพื่อเข้าใช้งานหลังบ้าน:", type="password", key=f"pwd_input_{session_key_name}")
            if st.button("ยืนยันรหัสผ่านเข้าสู่ระบบ", key=f"btn_auth_{session_key_name}"):
                if pwd == PASSWORD:
                    st.session_state[session_key_name] = True
                    st.rerun()
                else:
                    st.error("รหัสผ่านไม่ถูกต้อง โปรดลองอีกครั้ง")
            return False
    return True

# ==========================================
# 🌐 TAB 1: บอร์ดคู่มือภารกิจสาธารณะสำหรับนักศึกษา (เปิดเผย 100%)
# ==========================================
with tab1:
    st.header("📋 คู่มือภารกิจเมกะโปรเจ็ค & เช็กสถานะงานดิจิทัล")
    st.caption("นักศึกษาสามารถสแกนเข้ามาอ่านรายละเอียดเงื่อนไขและจองงานได้จากหน้านี้โดยไม่ต้องใช้กระดาษ")
    
    if MATERIAL_PRICES:
        with st.expander("📦 รายการวัสดุอุปกรณ์และราคากลาง (สำหรับวางแผนคำนวณต้นทุน)", expanded=True):
            mat_records = [{"รายการวัสดุ/อุปกรณ์": mat, "ราคากลาง (บาท)": f"{price:,}"} for mat, price in MATERIAL_PRICES.items()]
            df_mat = pd.DataFrame(mat_records)
            st.table(df_mat)

    st.markdown("---")

    if PROJECT_MASTER:
        p_options = sorted(list(PROJECT_MASTER.keys()), key=int)
        selected_p = st.selectbox("🔍 เลือกดูรายละเอียดโปรเจ็คที่ต้องการศึกษา:", p_options, 
                                   format_func=lambda x: f"โปรเจ็ครหัส {x} : {PROJECT_MASTER[x]['name']}")
        
        st.info(f"**📜 รายละเอียดข้อกำหนดโปรเจ็ค:** {PROJECT_MASTER[selected_p]['description']}")
        
        st.markdown("**📊 Status สถานะการจองในแต่ละระดับความยาก:**")
        lvl_records = []
        for lvl, ldata in PROJECT_MASTER[selected_p]["levels"].items():
            status_key = f"{selected_p}-{lvl}"
            current_status = STATUS_MAP.get(status_key, "ว่าง")
            lvl_records.append({
                "ระดับความยาก": f"ระดับ {lvl}",
                "เงื่อนไขเฉพาะ": ldata["condition"],
                "เงินรางวัลสัญญา (บาท)": f"{ldata['reward']:,}",
                "สถานะปัจจุบัน": current_status
            })
        df_lvl = pd.DataFrame(lvl_records)
        
        def color_status(val):
            if val == "ว่าง": return 'background-color: #d1e7dd; color: #0f5132; font-weight: bold;'
            if val == "กำลังดำเนินการ": return 'background-color: #fff3cd; color: #664d03; font-weight: bold;'
            return 'background-color: #f8d7da; color: #842029; text-decoration: line-through;'
        
        st.table(df_lvl.style.map(color_status, subset=['สถานะปัจจุบัน']))

# ==========================================
# 🔐 TAB 2: หลังบ้านเจ้าหน้าที่ควบคุมระบบ (Staff Only)
# ==========================================
if check_staff_authentication(tab2, "auth_tab2"):
    with tab2:
        # 📊 แบ่ง Layout อัตราส่วนหน้าจอเป็น [ 1 ส่วน | 2 ส่วน ] เพื่อเพิ่มพื้นที่ให้ตารางข้อมูลภาพรวม
        col_f, col_edit = st.columns([1, 2])
        
        # 📥 ฝั่งซ้าย (กว้าง 1 ส่วน): ลงทะเบียนโปรเจ็ค + สั่งซื้อวัสดุ
        with col_f:
            st.subheader("📝 1. ส่วนลงทะเบียนโปรเจ็ค")
            st.markdown("##### 📥 ฟอร์มลงทะเบียนและสั่งของใหม่")
            
            deal_choices = []
            for pid, pdata in PROJECT_MASTER.items():
                for lvl in pdata["levels"].keys():
                    key = f"{pid}-{lvl}"
                    if STATUS_MAP.get(key, "ว่าง") == "ว่าง":
                        deal_choices.append(key)
            
            if deal_choices:
                chosen_key = st.selectbox("เลือกโปรเจ็ค (รหัสโปรเจ็ค-ระดับ):", sorted(deal_choices, key=lambda x: (int(x.split('-')[0]), int(x.split('-')[1]))), 
                                          format_func=lambda x: f"งาน {x.split('-')[0]} {PROJECT_MASTER[x.split('-')[0]]['name']} (ระดับ {x.split('-')[1]})", key="new_deal_box")
                p_id, d_lvl = chosen_key.split("-")
                reward_amt = PROJECT_MASTER[p_id]["levels"][d_lvl]["reward"]
                
                st.markdown(f"💰 **มูลค่าสัญญาโปรเจ็ค:** `{reward_amt:,}` บาท")
                investor = st.selectbox("ทีมนักลงทุน:", TEAMS, index=0, key="new_inv")
                contractor = st.selectbox("ทีมผู้รับเหมา:", TEAMS, index=1, key="new_con")
                budget = st.number_input("งบประมาณที่ตกลงกันไว้ (บาท):", min_value=0, value=200000, key="new_budget")
                
                # 📈 สัดส่วนแบ่งกำไรแบบกรอกอิสระทั้งสองฝั่ง (Numeric Up-Down)
                st.markdown("📈 **สัดส่วนแบ่งกำไร นักลงทุน | ผู้รับเหมา (%)**")
                col_pct1, col_pct2 = st.columns(2)
                with col_pct1:
                    inv_pct = st.number_input("นักลงทุน", min_value=0, max_value=100, value=40, step=1, key="new_inv_pct")
                with col_pct2:
                    con_pct = st.number_input("ผู้รับเหมา", min_value=0, max_value=100, value=60, step=1, key="new_con_pct")
                
                # ตารางเปิดบิลคำนวณราคาวัสดุ
                mat_cost_calc = 0
                mat_order_details = {}
                if "reset_trigger" not in st.session_state:
                    st.session_state["reset_trigger"] = 0
                
                with st.expander("🛒 เปิดบิลคำนวณราคาวัสดุ (สั่งซื้อได้ครั้งเดียว)", expanded=False):
                    for mat, price in MATERIAL_PRICES.items():
                        qty = st.number_input(f"{mat} ({price:,} บ.)", min_value=0, value=0, key=f"order_{mat}_{st.session_state['reset_trigger']}")
                        mat_cost_calc += qty * price
                        mat_order_details[mat] = qty
                        
                    if st.button("🔄 ล้างรายการสั่งซื้อ (Reset เป็น 0 ทั้งหมด)", use_container_width=True):
                        st.session_state["reset_trigger"] += 1
                        st.rerun()
                        
                st.markdown(f"📦 **ราคารวมวัสดุสั่งซื้อสุทธิ:** `{mat_cost_calc:,}` บาท")
                
                if st.button("📥 ยืนยันการลงทะเบียนโปรเจ็ค", use_container_width=True):
                    busy_project = None
                    busy_idx = -1
                    for idx, deal in enumerate(GAME_DATA):
                        if deal["contractor"] == contractor and deal["result"] in ["รอตรวจ", "ไม่ผ่าน"]:
                            busy_project = f"โปรเจ็ค {deal['project_id']} (ระดับ {deal['difficulty']})"
                            busy_idx = idx + 1
                            break
                    
                    if investor == contractor: 
                        st.error("❌ ห้ามนักลงทุนและผู้รับเหมาเป็นทีมเดียวกันครับ")
                    elif inv_pct + con_pct != 100:
                        st.error(f"❌ สัดส่วนแบ่งกำไรรวมกันต้องได้ 100% พอดี (ปัจจุบันได้ {inv_pct + con_pct}%)")
                    elif busy_project is not None:
                        st.error(f"❌ ทีม **[{contractor}]** กำลังมีงานค้างดำเนินการอยู่ ({busy_project} ในคิวที่ {busy_idx}) ต้องส่งตรวจให้ผ่านหรือให้สตาฟลบแถวข้อมูลออกก่อนจึงจะจองงานใหม่ได้")
                    elif budget < mat_cost_calc:
                        st.error(f"❌ งบประมาณไม่เพียงพอ! งบประมาณตั้งต้นของโปรเจ็ค ({budget:,} บาท) จะต้องสูงกว่าหรือเท่ากับราคารวมวัสดุสั่งซื้อ ({mat_cost_calc:,} บาท) เสมอครับ")
                    else:
                        GAME_DATA.append({
                            "project_id": p_id, "project_name": PROJECT_MASTER[p_id]["name"],
                            "difficulty": int(d_lvl), "reward": reward_amt, "investor": investor,
                            "investor_pct": inv_pct, "contractor": contractor, "contractor_pct": con_pct,
                            "budget": budget, "material_cost": mat_cost_calc, "times": 0, "result": "รอตรวจ", "net_profit": 0,
                            "items_ordered": mat_order_details, "shop_received": False
                        })
                        save_json(DATA_FILE, GAME_DATA)
                        st.success("✅ บันทึกข้อมูลลงทะเบียนสำเร็จ!")
                        st.rerun()
            else:
                st.info("โปรเจ็คทุกระดับถูกจับจองหรือทำเสร็จสิ้นหมดแล้ว!")

        # 📊 ฝั่งขวา (กว้าง 2 ส่วน): แสดงตารางภาพรวมขนาดใหญ่ พร้อมระบบแก้ไข/ลบ/ขอยกเลิก
        with col_edit:
            st.subheader("📊 ตารางภาพรวมข้อมูลโปรเจ็ค")
            st.markdown("##### 🔍 ค้นหา แก้ไข หรือลบข้อมูลดีลงานที่คีย์ผิด")
            if GAME_DATA:
                df_overview = pd.DataFrame(GAME_DATA)
                display_cols = ["project_id", "difficulty", "investor", "investor_pct", "contractor", "contractor_pct", "material_cost", "budget", "result"]
                df_display = df_overview[display_cols].copy()
                df_display.columns = ["รหัส", "ระดับ", "นักลงทุน", "กำไรนายทุน %", "ผู้รับเหมา", "กำไรผู้รับเหมา %", "ค่าวัสดุ", "งบลงทุน", "สถานะผล"]
                
                # 🛠️ [จุดแก้ไข] ดึงระบบ State Machine ฝังคำห้อยท้ายสถานะใน Dropdown ค้นหาและแก้ไขคิวงาน
                selected_row_idx = st.selectbox(
                    "🎯 คลิกเลือกแถวคิวงานที่ต้องการ แก้ไข/ลบถาวร/ขอยกเลิก:", 
                    range(len(GAME_DATA)), 
                    format_func=lambda x: f"คิวที่ {x + 1} | โปรเจ็ค {GAME_DATA[x]['project_id']} (ระดับ {GAME_DATA[x]['difficulty']}) -> ทีม {GAME_DATA[x]['contractor']}" + get_deal_status_label(GAME_DATA[x])
                )
                
                target_edit = GAME_DATA[selected_row_idx]
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    with st.expander("✏️ ฟอร์มแก้ไขข้อมูล / 🗑️ ลบ Record คีย์ผิดพลาด"):
                        st.text_input("🎯 คิวที่ทำงานปัจจุบัน (Read-Only):", value=str(selected_row_idx + 1), disabled=True)
                        
                        edit_inv = st.selectbox("แก้ไขนักลงทุน:", TEAMS, index=TEAMS.index(target_edit["investor"]), key=f"ed_inv_{selected_row_idx}")
                        
                        st.markdown("⚡ *แก้ไขสัดส่วนแบ่งกำไร (%)*")
                        col_ed_p1, col_ed_p2 = st.columns(2)
                        with col_ed_p1:
                            edit_inv_pct = st.number_input("นักลงทุน", min_value=0, max_value=100, value=int(target_edit["investor_pct"]), key=f"ed_inv_pct_{selected_row_idx}")
                        with col_ed_p2:
                            edit_con_pct = st.number_input("ผู้รับเหมา", min_value=0, max_value=100, value=int(target_edit["contractor_pct"]), key=f"ed_con_pct_{selected_row_idx}")
                            
                        edit_con = st.selectbox("แก้ไขผู้รับเหมา:", TEAMS, index=TEAMS.index(target_edit["contractor"]), key=f"ed_con_{selected_row_idx}")
                        edit_bug = st.number_input("แก้ไขงบลงทุน:", min_value=0, value=int(target_edit["budget"]), key=f"ed_bug_{selected_row_idx}")
                        edit_mat = st.number_input("แก้ไขราคารวมวัสดุ:", min_value=0, value=int(target_edit["material_cost"]), key=f"ed_mat_{selected_row_idx}")
                        
                        if st.button("💾 บันทึกการแก้ไขข้อมูล", key=f"btn_save_ed_{selected_row_idx}", use_container_width=True):
                            if edit_inv_pct + edit_con_pct != 100:
                                st.error(f"❌ บันทึกไม่ได้! สัดส่วนแก้ไขรวมกันต้องได้ 100% พอดี (ปัจจุบันได้ {edit_inv_pct + edit_con_pct}%)")
                            elif edit_bug < edit_mat:
                                st.error(f"❌ งบประมาณแก้ไขไม่เพียงพอ! งบลงทุน ({edit_bug:,} บ.) ต้องมากกว่าราคาของวัสดุ ({edit_mat:,} บ.)")
                            else:
                                GAME_DATA[selected_row_idx].update({
                                    "investor": edit_inv, "investor_pct": edit_inv_pct, 
                                    "contractor": edit_con, "contractor_pct": edit_con_pct, 
                                    "budget": edit_bug, "material_cost": edit_mat
                                })
                                save_json(DATA_FILE, GAME_DATA)
                                st.success("แก้ไขข้อมูลในระบบเรียบร้อย!")
                                st.rerun()
                        
                        st.markdown("---")
                        confirm_key = f"confirm_delete_{selected_row_idx}"
                        if confirm_key not in st.session_state:
                            st.session_state[confirm_key] = False
                            
                        if not st.session_state[confirm_key]:
                            if st.button("🗑️ ลบ Record นี้ออกจากระบบถาวร (Staff Only)", key=f"btn_del_click_{selected_row_idx}", use_container_width=True):
                                st.session_state[confirm_key] = True
                                st.rerun()
                        else:
                            st.warning(f"⚠️ **คุณแน่ใจใช่ไหม?** ระบบจะทำการลบข้อมูลคิวที่ {selected_row_idx + 1} ออกจากฐานข้อมูลทันทีแบบกู้คืนไม่ได้!")
                            col_conf1, col_conf2 = st.columns(2)
                            with col_conf1:
                                if st.button("✅ ใช่, ยืนยันการลบถาวร", key=f"btn_yes_{selected_row_idx}", use_container_width=True, type="primary"):
                                    GAME_DATA.pop(selected_row_idx)
                                    save_json(DATA_FILE, GAME_DATA)
                                    st.session_state[confirm_key] = False
                                    st.success("🗑️ ลบข้อมูลออกจากระบบถาวรเสร็จสิ้น!")
                                    st.rerun()
                            with col_conf2:
                                if st.button("❌ ยกเลิก", key=f"btn_no_{selected_row_idx}", use_container_width=True):
                                    st.session_state[confirm_key] = False
                                    st.rerun()
                            
                with col_btn2:
                    if target_edit["result"] not in ["ผ่าน", "ยกเลิก"]:
                        cancel_confirm_key = f"cancel_confirm_{selected_row_idx}"
                        if cancel_confirm_key not in st.session_state:
                            st.session_state[cancel_confirm_key] = False
                            
                        if not st.session_state[cancel_confirm_key]:
                            if st.button("🚨 ขอยกเลิกโปรเจ็คนี้ (โดยความต้องการของทีม)", type="primary", key=f"btn_cancel_click_{selected_row_idx}", use_container_width=True):
                                st.session_state[cancel_confirm_key] = True
                                st.rerun()
                        else:
                            st.error(f"⚠️ **ยืนยันการหักยอดบัญชีนายทุน?** หากยกเลิกคิวที่ {selected_row_idx + 1} ทีมนายทุนจะถูกปรับติดลบก้อนเงินลงทุนทันที **-{int(target_edit['budget'])}** บาท!")
                            col_cc1, col_conf2 = st.columns(2)
                            with col_cc1:
                                if st.button("🚨 ใช่, ยืนยันการยกเลิก", key=f"btn_yes_cancel_{selected_row_idx}", use_container_width=True, type="primary"):
                                    GAME_DATA[selected_row_idx]["result"] = "ยกเลิก"
                                    GAME_DATA[selected_row_idx]["net_profit"] = -int(target_edit["budget"])
                                    save_json(DATA_FILE, GAME_DATA)
                                    st.session_state[cancel_confirm_key] = False
                                    st.warning("⚠️ เปลี่ยนสถานะเป็นยกเลิกและตัดยอดเงินทุนเรียบร้อย!")
                                    st.rerun()
                            with col_conf2:
                                if st.button("❌ กลับไปหน้าเดิม", key=f"btn_no_cancel_{selected_row_idx}", use_container_width=True):
                                    st.session_state[cancel_confirm_key] = False
                                    st.rerun()
                
                df_display.index = range(1, len(df_display) + 1)
                st.dataframe(df_display, use_container_width=True)
            else:
                st.info("ยังไม่มีข้อมูลลงทะเบียนในระบบ")

        # ⏱️ ส่วนบันทึกผลการตรวจงาน (ส่วนที่ 2 ด้านล่างของแท็บ 2)
        st.markdown("---")
        st.subheader("⏱️ 2. ส่วนบันทึกผลการตรวจ")
        
        pending_indices = [idx for idx, r in enumerate(GAME_DATA) if r["result"] in ["รอตรวจ", "ไม่ผ่าน"]]
        
        if pending_indices:
            df_pending = pd.DataFrame([GAME_DATA[i] for i in pending_indices])[["project_id", "difficulty", "investor", "contractor", "material_cost", "budget", "result"]]
            df_pending.columns = ["รหัสโปรเจ็ค", "ระดับความยาก", "ทีมนักลงทุน", "ทีมผู้รับเหมา", "ราคารวมวัสดุเดิม", "งบประมาณโปรเจ็ค", "ผลตรวจรอบล่าสุด"]
            st.markdown("*ตารางสรุปข้อมูลรายการโปรเจ็คทำกำลังดำเนินการทั้งหมด สามารถกดเลือกคลิก Row ด้านล่างเพื่อทำการบันทึกตรวจงาน:*")
            st.dataframe(df_pending, use_container_width=True, hide_index=True)
            
            # 🛠️ [จุดแก้ไข] ดึงระบบ State Machine ฝังคำห้อยท้ายสถานะใน Dropdown บันทึกผลตรวจงาน
            audit_idx = st.selectbox(
                "🔍 คลิกเลือกแถวข้อมูลโปรเจ็คเพื่อทำการบันทึกผลการตรวจงาน:", 
                pending_indices,
                format_func=lambda x: f"คิวที่ {x + 1} | โปรเจ็ค {GAME_DATA[x]['project_id']} (ระดับ {GAME_DATA[x]['difficulty']}) -> ผู้รับเหมา: {GAME_DATA[x]['contractor']}" + get_deal_status_label(GAME_DATA[x])
            )
            
            target_audit = GAME_DATA[audit_idx]
            
            previous_audit_fee = int(target_audit.get("times", 0)) * 2000
            current_balance = int(target_audit["budget"]) - int(target_audit["material_cost"]) - previous_audit_fee
            
            st.markdown(f"💳 **ตรวจสอบสถานะงบดุลบัญชีโปรเจ็ค:**")
            st.markdown(f"- งบประมาณก้อนลงทุนของโปรเจ็ค: `{target_audit['budget']:,}` บาท | - หักต้นทุนราคาของวัสดุรวม: `{target_audit['material_cost']:,}` บาท")
            st.markdown(f"- ส่งเข้าตรวจสะสมมาแล้ว: `{target_audit['times']}` ครั้ง (ตัดยอดงบประมาณตรวจไปแล้ว `{previous_audit_fee:,}` บาท)")
            st.error(f"💰 ยอดเงินทุนคงเหลือสุทธิของโปรเจ็คปัจจุบัน: **{current_balance:,}** บาท (ระบบเตรียมทำการหักยอดตัดสิทธิ์ค่าตรวจรอบนี้เพิ่มอีก **2,000** บาท)")
            
            col_au1, col_au2 = st.columns(2)
            with col_au1:
                next_time_count = int(target_audit.get("times", 0)) + 1
                st.number_input("ครั้งที่ตรวจ (ระบบรันให้อัตโนมัติ):", value=next_time_count, disabled=True, key="display_times")
            with col_au2:
                eval_result = st.selectbox("ผลลัพธ์การตรวจสอบงานรอบนี้:", ["ผ่าน", "ไม่ผ่าน"], key="eval_result_box")
                
            if st.button("💾 ยืนยันการบันทึกผลการตรวจงานรอบนี้", type="primary", use_container_width=True):
                GAME_DATA[audit_idx]["times"] = next_time_count
                total_spent = int(target_audit["material_cost"]) + (next_time_count * 2000)
                
                if eval_result == "ผ่าน":
                    GAME_DATA[audit_idx]["result"] = "ผ่าน"
                    GAME_DATA[audit_idx]["net_profit"] = int(target_audit["reward"]) - total_spent
                    st.success(f"🎉 ตรวจงานผ่านแล้ว! โปรเจ็คเปลี่ยนสถานะเป็น [เสร็จสิ้น] และระบบทำการล็อกความยากระดับนี้เรียบร้อย")
                else:
                    GAME_DATA[audit_idx]["result"] = "ไม่ผ่าน"
                    st.warning(f"❌ ผลการตรวจงานรอบนี้คือ [ไม่ผ่าน] โปรเจ็คยังอยู่ในระบบ สามารถส่งตรวจใหม่ครั้งถัดไปได้")
                    
                save_json(DATA_FILE, GAME_DATA)
                st.rerun()
        else:
            st.info("🎉 ไม่มีโปรเจ็คทำกำลังดำเนินการอยู่ (รอตรวจ) ในระบบขณะนี้")

        # 💾 ระบบสำรองข้อมูล
        st.markdown("---")
        st.subheader("💾 ระบบรักษาความปลอดภัยข้อมูล")
        col_bk1, col_bk2 = st.columns(2)
        with col_bk1:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                current_data_str = f.read()
            st.download_button(label="📥 ดาวน์โหลดไฟล์สำรองข้อมูลล่าสุด (Backup)", data=current_data_str, file_name="Mega_Project_Backup.json", mime="application/json")
        with col_bk2:
            uploaded_backup = st.file_uploader("📂 กู้คืนสถานะคะแนนและดีล (Restore)", type=["json"])
            if uploaded_backup is not None:
                if st.button("🔄 ยืนยันคำสั่งกู้คืนระบบ"):
                    backup_data = json.load(uploaded_backup)
                    save_json(DATA_FILE, backup_data)
                    st.success("✅ กู้คืนระบบบัญชีหน้างานสำเร็จ!")
                    st.rerun()

# ==========================================
# 🏪 TAB 4: หลังบ้านสตาฟคุมร้านค้าวัสดุอุปกรณ์ (Shop Only) - ล็อกรหัสผ่าน
# ==========================================
if check_staff_authentication(tab4, "auth_tab4"):
    with tab4:
        st.header("🏪 เคาน์เตอร์ตรวจเช็คและจัดส่งวัสดุกิจกรรม")
        st.caption("สตาฟประจำซุ้มของเล่น สามารถตรวจดูลิสต์สิ่งของตามใบเปิดบิลของแต่ละทีม และกดยืนยันเมื่อส่งมอบของครบถ้วน")
        
        uncompleted_shop_deals = [idx for idx, deal in enumerate(GAME_DATA) if deal["result"] != "ยกเลิก" and not deal.get("shop_received", False)]
        
        if uncompleted_shop_deals:
            st.subheader("🛒 1. คิวงานเบิกพัสดุอุปกรณ์ที่รอจัดส่ง")
            
            # 🛠️ [จุดแก้ไข] ดึงระบบ State Machine ฝังคำห้อยท้ายสถานะใน Dropdown หน้าร้านค้าเบิกจ่ายของ
            shop_select_idx = st.selectbox(
                "🎯 เลือกคิวงานเพื่อดูรายการวัสดุที่ต้องจัดให้เด็ก:",
                uncompleted_shop_deals,
                format_func=lambda x: f"คิวที่ {x + 1} | ทีมผู้รับเหมา: {GAME_DATA[x]['contractor']} -> จองโปรเจ็ค {GAME_DATA[x]['project_id']} (ระดับ {GAME_DATA[x]['difficulty']})" + get_deal_status_label(GAME_DATA[x])
            )
            
            target_shop_deal = GAME_DATA[shop_select_idx]
            ordered_items_dict = target_shop_deal.get("items_ordered", {})
            
            st.markdown(f"📦 **รายการบิลวัสดุของทีม [{target_shop_deal['contractor']}] (โปรเจ็ค {target_shop_deal['project_id']} ระดับ {target_shop_deal['difficulty']}):**")
            
            shop_records = []
            for mat_name, qty in ordered_items_dict.items():
                if qty > 0:
                    shop_records.append({"รายการวัสดุอุปกรณ์": mat_name, "จำนวนที่สั่งซื้อ": f"{qty:,} ชิ้น"})
            
            if shop_records:
                df_shop_bill = pd.DataFrame(shop_records)
                st.table(df_shop_bill)
                
                if st.button(f"✅ ยืนยันว่าทีม [{target_shop_deal['contractor']}] มารับของครบเรียบร้อยแล้ว", type="primary", use_container_width=True):
                    GAME_DATA[shop_select_idx]["shop_received"] = True
                    save_json(DATA_FILE, GAME_DATA)
                    st.success(f"📦 บันทึกสถานะการส่งมอบของให้ทีม {target_shop_deal['contractor']} สำเร็จ!")
                    st.rerun()
            else:
                st.info("โปรเจ็คคิวนี้ไม่มีการสั่งซื้อวัสดุเพิ่มเติมในระบบบิล (งบค่าของเป็น 0)")
                if st.button(f"✅ ยืนยันการผ่านสิทธิ์คิวนี้ (ไม่มีของต้องจ่าย)", use_container_width=True):
                    GAME_DATA[shop_select_idx]["shop_received"] = True
                    save_json(DATA_FILE, GAME_DATA)
                    st.rerun()
        else:
            st.info("🎉 สบายแล้ว! ปัจจุบันไม่มีคิวสั่งของค้างจ่ายในระบบ หรือทุกทีมเข้ามารับวัสดุอุปกรณ์ไปครบถ้วนหมดแล้วครับ")

        st.markdown("---")
        st.subheader("📋 2. ประวัติการรับพัสดุอุปกรณ์ที่เสร็จสิ้นแล้ว")
        completed_shop_records = []
        for idx, deal in enumerate(GAME_DATA):
            if deal.get("shop_received", False):
                items_summary = ", ".join([f"{k} ({v} ชิ้น)" for k, v in deal.get("items_ordered", {}).items() if v > 0])
                completed_shop_records.append({
                    "คิวที่": idx + 1,
                    "ทีมผู้รับเหมา": deal["contractor"],
                    "โปรเจ็ค-ระดับ": f"{deal['project_id']} (ระดับ {deal['difficulty']})",
                    "รายการพัสดุที่รับไป": items_summary if items_summary else "ไม่เบิกของ",
                    "สถานะ": "🟢 รับของแล้ว"
                })
        if completed_shop_records:
            st.dataframe(pd.DataFrame(completed_shop_records), use_container_width=True, hide_index=True)

# ==========================================
# 🏆 TAB 3: ลีดเดอร์บอร์ดจัดอันดับคะแนน (Staff Only) - ล็อกรหัสผ่าน + อัปเกรดสถิติ
# ==========================================
if check_staff_authentication(tab3, "auth_tab3"):
    with tab3:
        st.header("🏆 อันดับคะแนนลีดเดอร์บอร์ดและแดชบอร์ดสถิติหน้างาน")
        st.caption("ข้อมูลวิเคราะห์ดุลบัญชีและประสิทธิภาพการลงทุนของแต่ละทีมสี")
        
        scores = {t: {"กำไรบทบาทนายทุน": 0, "กำไรบทบาทผู้รับเหมา": 0, "กำไรสุทธิรวม": 0, "ต้นทุนวัสดุสะสม": 0} for t in TEAMS}
        
        for d in GAME_DATA:
            if d["result"] in ["ผ่าน", "ยกเลิก"]:
                if d["result"] == "ผ่าน":
                    scores[d["investor"]]["กำไรบทบาทนายทุน"] += d["net_profit"] * (d["investor_pct"]/100)
                    scores[d["contractor"]]["กำไรบทบาทผู้รับเหมา"] += d["net_profit"] * (d["contractor_pct"]/100)
                    scores[d["investor"]]["ต้นทุนวัสดุสะสม"] += d["material_cost"]
                elif d["result"] == "ยกเลิก":
                    scores[d["investor"]]["กำไรบทบาทนายทุน"] += d["net_profit"]
                    
        for t in TEAMS: 
            scores[t]["กำไรสุทธิรวม"] = scores[t]["กำไรบทบาทนายทุน"] + scores[t]["กำไรบทบาทผู้รับเหมา"]
            
        if len(GAME_DATA) > 0:
            df_sc = pd.DataFrame.from_dict(scores, orient='index').sort_values(by="กำไรสุทธิรวม", ascending=False)
            
            if df_sc.iloc[0]["กำไรสุทธิรวม"] != 0:
                st.metric(label=f"👑 สีที่เป็นผู้นำตลาดในขณะนี้คิอ:", value=f"ทีม {df_sc.index[0]} ({df_sc.iloc[0]['กำไรสุทธิรวม']:,.0f} บาท)")
            
            col_table, col_chart = st.columns([1, 1.2])
            
            with col_table:
                st.markdown("##### 📊 ตารางดุลบัญชีสุทธิสะสม")
                st.dataframe(df_sc.style.format("{:,.0f}"), use_container_width=True)
                
            with col_chart:
                st.markdown("##### 📈 1. แผนภูมิแท่งเปรียบเทียบกำไรสุทธิรวม")
                st.bar_chart(df_sc["กำไรสุทธิรวม"])
                
            st.markdown("---")
            st.subheader("📊 สถิติวิเคราะห์เชิงลึกสำหรับบรีฟสรุปกิจกรรม (Debriefing)")
            
            col_analysis1, col_analysis2 = st.columns(2)
            
            with col_analysis1:
                st.markdown("##### 🤝 ประสิทธิภาพจำแนกตามบทบาท (นายทุน vs ผู้รับเหมา)")
                df_role = df_sc[["กำไรบทบาทนายทุน", "กำไรบทบาทผู้รับเหมา"]]
                st.bar_chart(df_role)
                st.caption("💡 แผนภูมินี้ช่วยวิเคราะห์ว่าทีมสีใดมีทักษะโดดเด่นด้าน 'การเจรจาลงทุน (นายทุน)' หรือด้าน 'การควบคุมการผลิต (ผู้รับเหมา)'")
                
            with col_analysis2:
                st.markdown("##### 🛒 สัดส่วนมูลค่าการลงทุนซื้อพัสดุในตลาดกลาง")
                df_mat_share = df_sc[df_sc["ต้นทุนวัสดุสะสม"] > 0]["ต้นทุนวัสดุสะสม"]
                if not df_mat_share.empty:
                    st.bar_chart(df_mat_share)
                    st.caption("💡 แสดงปริมาณเงินสะสมที่แต่ละทีมใช้ในการหมุนเวียนซื้อวัสดุอุปกรณ์จากร้านค้ากลาง")
                else:
                    st.info("ยังไม่มีทีมใดทำโปรเจ็คผ่านระบบสั่งของสำเร็จ จึงยังไม่มีสถิติมูลค่าตลาดพัสดุ")
        else:
            st.info("ยังไม่มีข้อมูลใบลงทะเบียนปิดจ๊อบสรุปผลบัญชีในระบบขณะนี้")
