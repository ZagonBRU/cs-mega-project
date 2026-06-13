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

# ประมวลผลหา "สถานะปัจจุบัน" ของโปรเจกต์แต่ละระดับความยากแบบ Dynamic
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
tab1, tab2, tab3 = st.tabs(["🌐 คู่มือและบอร์ดสถานะโครงการ (สำหรับนักศึกษา)", "🔐 ระบบควบคุมเกม (Staff Only)", "🏆 สรุปคะแนนลีดเดอร์บอร์ด"])

# ==========================================
# 🌐 TAB 1: บอร์ดคู่มือภารกิจสาธารณะสำหรับนักศึกษา
# ==========================================
with tab1:
    st.header("📋 คู่มือภารกิจเมกะโปรเจกต์ & เช็กสถานะงานดิจิทัล")
    st.caption("นักศึกษาสามารถสแกนเข้ามาอ่านรายละเอียดเงื่อนไขและจองงานได้จากหน้านี้โดยไม่ต้องใช้กระดาษ")
    
    # 💡 [จุดเพิ่มที่ 1] เพิ่มการแสดงรายการวัสดุและราคากลางฝั่งนักศึกษา เพื่อให้ทุกทีมใช้วางแผนต้นทุนก่อนเดินมาหาตาฟ
    if MATERIAL_PRICES:
        with st.expander("📦 รายการวัสดุอุปกรณ์และราคากลาง (สำหรับวางแผนคำนวณต้นทุน)", expanded=True):
            mat_records = [{"รายการวัสดุ/อุปกรณ์": mat, "ราคากลาง (บาท)": f"{price:,}"} for mat, price in MATERIAL_PRICES.items()]
            df_mat = pd.DataFrame(mat_records)
            st.table(df_mat)
            st.caption("⚠️ หมายเหตุ: รายการที่มีเครื่องหมาย * เป็นวัสดุควบคุมตามข้อกำหนดเฉพาะของบางโครงการ โปรดตรวจสอบเงื่อนไขก่อนสั่งซื้อ")

    st.markdown("---")

    if PROJECT_MASTER:
        p_options = sorted(list(PROJECT_MASTER.keys()), key=int)
        selected_p = st.selectbox("🔍 เลือกดูรายละเอียดโครงการที่ต้องการศึกษา:", p_options, 
                                   format_func=lambda x: f"โพรเจกต์รหัส {x} : {PROJECT_MASTER[x]['name']}")
        
        st.info(f"**📜 รายละเอียดข้อกำหนดโครงการ:** {PROJECT_MASTER[selected_p]['description']}")
        
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
with tab2:
    if "auth" not in st.session_state: st.session_state["auth"] = False
    if not st.session_state["auth"]:
        pwd = st.text_input("กรอกรหัสผ่านควบคุมระบบ:", type="password")
        if st.button("เข้าสู่หลังบ้าน"):
            if pwd == PASSWORD: st.session_state["auth"] = True; st.rerun()
            else: st.error("รหัสผ่านไม่ถูกต้อง")
    else:
        # 📊 Layout [ 1 ส่วน | 2 ส่วน ]
        col_f, col_edit = st.columns([1, 2])
        
        # 📥 ฝั่งซ้าย (กว้าง 1 ส่วน): ลงทะเบียนโครงการ + สั่งซื้อวัสดุ
        with col_f:
            st.subheader("📝 1. ส่วนลงทะเบียนโครงการ")
            st.markdown("##### 📥 ฟอร์มลงทะเบียนและสั่งของใหม่")
            
            deal_choices = []
            for pid, pdata in PROJECT_MASTER.items():
                for lvl in pdata["levels"].keys():
                    key = f"{pid}-{lvl}"
                    if STATUS_MAP.get(key, "ว่าง") == "ว่าง":
                        deal_choices.append(key)
            
            if deal_choices:
                chosen_key = st.selectbox("เลือกโครงการ (รหัสโครงการ-ระดับ):", sorted(deal_choices, key=lambda x: (int(x.split('-')[0]), int(x.split('-')[1]))), 
                                          format_func=lambda x: f"งาน {x.split('-')[0]} {PROJECT_MASTER[x.split('-')[0]]['name']} (ระดับ {x.split('-')[1]})", key="new_deal_box")
                p_id, d_lvl = chosen_key.split("-")
                reward_amt = PROJECT_MASTER[p_id]["levels"][d_lvl]["reward"]
                
                st.markdown(f"💰 **มูลค่าสัญญาโครงการ:** `{reward_amt:,}` บาท")
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
                if "reset_trigger" not in st.session_state:
                    st.session_state["reset_trigger"] = 0
                
                with st.expander("🛒 เปิดบิลคำนวณราคาวัสดุ (สั่งซื้อได้ครั้งเดียว)", expanded=False):
                    for mat, price in MATERIAL_PRICES.items():
                        qty = st.number_input(f"{mat} ({price:,} บ.)", min_value=0, value=0, key=f"order_{mat}_{st.session_state['reset_trigger']}")
                        mat_cost_calc += qty * price
                        
                    if st.button("🔄 ล้างรายการสั่งซื้อ (Reset เป็น 0 ทั้งหมด)", use_container_width=True):
                        st.session_state["reset_trigger"] += 1
                        st.rerun()
                        
                st.markdown(f"📦 **ราคารวมวัสดุสั่งซื้อสุทธิ:** `{mat_cost_calc:,}` บาท")
                
                if st.button("📥 ยืนยันการลงทะเบียนโครงการ", use_container_width=True):
                    busy_project = None
                    busy_idx = -1
                    for idx, deal in enumerate(GAME_DATA):
                        if deal["contractor"] == contractor and deal["result"] in ["รอตรวจ", "ไม่ผ่าน"]:
                            busy_project = f"โพรเจกต์ {deal['project_id']} (ระดับ {deal['difficulty']})"
                            busy_idx = idx
                            break
                    
                    if investor == contractor: 
                        st.error("❌ ห้ามนักลงทุนและผู้รับเหมาเป็นทีมเดียวกันครับ")
                    elif inv_pct + con_pct != 100:
                        st.error(f"❌ สัดส่วนแบ่งกำไรรวมกันต้องได้ 100% พอดี (ปัจจุบันได้ {inv_pct + con_pct}%)")
                    elif busy_project is not None:
                        st.error(f"❌ ทีม **[{contractor}]** กำลังมีงานค้างดำเนินการอยู่ ({busy_project} ในคิวที่ {busy_idx}) ต้องส่งตรวจให้ผ่านหรือให้สตาฟลบแถวข้อมูลออกก่อนจึงจะจองงานใหม่ได้")
                    elif budget < mat_cost_calc:
                        st.error(f"❌ งบประมาณไม่เพียงพอ! งบประมาณตั้งต้นของโครงการ ({budget:,} บาท) จะต้องสูงกว่าหรือเท่ากับราคารวมวัสดุสั่งซื้อ ({mat_cost_calc:,} บาท) เสมอครับ")
                    else:
                        GAME_DATA.append({
                            "project_id": p_id, "project_name": PROJECT_MASTER[p_id]["name"],
                            "difficulty": int(d_lvl), "reward": reward_amt, "investor": investor,
                            "investor_pct": inv_pct, "contractor": contractor, "contractor_pct": con_pct,
                            "budget": budget, "material_cost": mat_cost_calc, "times": 0, "result": "รอตรวจ", "net_profit": 0
                        })
                        save_json(DATA_FILE, GAME_DATA)
                        st.success("✅ บันทึกข้อมูลลงทะเบียนสำเร็จ!")
                        st.rerun()
            else:
                st.info("โครงการทุกระดับถูกจับจองหรือทำเสร็จสิ้นหมดแล้ว!")

        # 📊 ฝั่งขวา (กว้าง 2 ส่วน): แสดงตารางภาพรวมขนาดใหญ่ พร้อมระบบแก้ไข/ลบ/ขอยกเลิก
        with col_edit:
            st.subheader("📊 ตารางภาพรวมข้อมูลโครงการ")
            st.markdown("##### 🔍 ค้นหา แก้ไข หรือลบข้อมูลดีลงานที่คีย์ผิด")
            if GAME_DATA:
                df_overview = pd.DataFrame(GAME_DATA)
                display_cols = ["project_id", "difficulty", "investor", "investor_pct", "contractor", "contractor_pct", "material_cost", "budget", "result"]
                df_display = df_overview[display_cols].copy()
                df_display.columns = ["รหัส", "ระดับ", "นักลงทุน", "กำไรนายทุน %", "ผู้รับเหมา", "กำไรผู้รับเหมา %", "ค่าวัสดุ", "งบลงทุน", "สถานะผล"]
                
                selected_row_idx = st.selectbox("🎯 คลิกเลือกแถวคิวงานที่ต้องการ แก้ไข/ลบถาวร/ขอยกเลิก:", range(len(GAME_DATA)), 
                                                 format_func=lambda x: f"คิวที่ {x} | โพรเจกต์ {GAME_DATA[x]['project_id']} (ระดับ {GAME_DATA[x]['difficulty']}) -> ทีม {GAME_DATA[x]['contractor']}")
                
                target_edit = GAME_DATA[selected_row_idx]
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    with st.expander("✏️ ฟอร์มแก้ไขข้อมูล / 🗑️ ลบ Record คีย์ผิดพลาด"):
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
                            st.warning(f"⚠️ **คุณแน่ใจใช่ไหม?** ระบบจะทำการลบข้อมูลคิวที่ {selected_row_idx} ออกจากฐานข้อมูลทันทีแบบกู้คืนไม่ได้!")
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
                        if st.button("🚨 ขอยกเลิกโครงการนี้ (โดยความต้องการของทีม)", type="primary", key=f"btn_cancel_{selected_row_idx}", use_container_width=True):
                            GAME_DATA[selected_row_idx]["result"] = "ยกเลิก"
                            GAME_DATA[selected_row_idx]["net_profit"] = -int(target_edit["budget"])
                            save_json(DATA_FILE, GAME_DATA)
                            st.warning("⚠️ เปลี่ยนสถานะเป็นยกเลิกแล้ว (ทีมนายทุนสูญเสียเงินลงทุนก้อนแรกเรียบร้อย ประวัติการจองยังคงอยู่ในตาราง)")
                            st.rerun()
                
                st.dataframe(df_display, use_container_width=True)
            else:
                st.info("ยังไม่มีข้อมูลลงทะเบียนในระบบ")

        # ---------------------------------------------------------
        # ⏱️ ส่วนที่ 3: บันทึกผลการตรวจงาน
        # ---------------------------------------------------------
        st.markdown("---")
        st.subheader("⏱️ 2. ส่วนบันทึกผลการตรวจ")
        
        pending_indices = [idx for idx, r in enumerate(GAME_DATA) if r["result"] in ["รอตรวจ", "ไม่ผ่าน"]]
        
        if pending_indices:
            df_pending = pd.DataFrame([GAME_DATA[i] for i in pending_indices])[["project_id", "difficulty", "investor", "contractor", "material_cost", "budget", "result"]]
            df_pending.columns = ["รหัสโครงการ", "ระดับความยาก", "ทีมนักลงทุน", "ทีมผู้รับเหมา", "ราคารวมวัสดุเดิม", "งบประมาณโครงการ", "ผลตรวจรอบล่าสุด"]
            st.markdown("*ตารางสรุปข้อมูลรายการโครงการทำกำลังดำเนินการทั้งหมด สามารถกดเลือกคลิก Row ด้านล่างเพื่อทำการบันทึกตรวจงาน:*")
            st.dataframe(df_pending, use_container_width=True, hide_index=True)
            
            audit_idx = st.selectbox("🔍 คลิกเลือกแถวข้อมูลโครงการเพื่อทำการบันทึกผลการตรวจงาน:", pending_indices,
                                     format_func=lambda x: f"คิวที่ {x} | โพรเจกต์ {GAME_DATA[x]['project_id']} (ระดับ {GAME_DATA[x]['difficulty']}) -> ผู้รับเหมา: {GAME_DATA[x]['contractor']}")
            
            target_audit = GAME_DATA[audit_idx]
            
            previous_audit_fee = int(target_audit.get("times", 0)) * 2000
            current_balance = int(target_audit["budget"]) - int(target_audit["material_cost"]) - previous_audit_fee
            
            st.markdown(f"💳 **ตรวจสอบสถานะงบดุลบัญชีโครงการ:**")
            st.markdown(f"- งบประมาณก้อนลงทุนของโครงการ: `{target_audit['budget']:,}` บาท | - หักต้นทุนราคาของวัสดุรวม: `{target_audit['material_cost']:,}` บาท")
            st.markdown(f"- ส่งเข้าตรวจสะสมมาแล้ว: `{target_audit['times']}` ครั้ง (ตัดยอดงบประมาณตรวจไปแล้ว `{previous_audit_fee:,}` บาท)")
            st.error(f"💰 ยอดเงินทุนคงเหลือสุทธิของโครงการปัจจุบัน: **{current_balance:,}** บาท (ระบบเตรียมทำการหักยอดตัดสิทธิ์ค่าตรวจรอบนี้เพิ่มอีก **2,000** บาท)")
            
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
                    st.success(f"🎉 ตรวจงานผ่านแล้ว! โครงการเปลี่ยนสถานะเป็น [เสร็จสิ้น] และระบบทำการล็อกความยากระดับนี้เรียบร้อย")
                else:
                    GAME_DATA[audit_idx]["result"] = "ไม่ผ่าน"
                    st.warning(f"❌ ผลการตรวจงานรอบนี้คือ [ไม่ผ่าน] โครงการยังอยู่ในระบบ สามารถส่งตรวจใหม่ครั้งถัดไปได้")
                    
                save_json(DATA_FILE, GAME_DATA)
                st.rerun()
        else:
            st.info("🎉 ไม่มีโครงการทำกำลังดำเนินการอยู่ (รอตรวจ) ในระบบขณะนี้")

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
# 🏆 TAB 3: ลีดเดอร์บอร์ดจัดอันดับคะแนน
# ==========================================
with tab3:
    st.header("🏆 อันดับคะแนนลีดเดอร์บอร์ดสดหน้างาน")
    scores = {t: {"กำไรบทบาทนายทุน": 0, "กำไรบทบาทผู้รับเหมา": 0, "กำไรสุทธิรวม": 0} for t in TEAMS}
    for d in GAME_DATA:
        if d["result"] in ["ผ่าน", "ยกเลิก"]:
            if d["result"] == "ผ่าน":
                scores[d["investor"]]["กำไรบทบาทนายทุน"] += d["net_profit"] * (d["investor_pct"]/100)
                scores[d["contractor"]]["กำไรบทบาทผู้รับเหมา"] += d["net_profit"] * (d["contractor_pct"]/100)
            elif d["result"] == "ยกเลิก":
                scores[d["investor"]]["กำไรบทบาทนายทุน"] += d["net_profit"]
                
    for t in TEAMS: 
        scores[t]["กำไรสุทธิรวม"] = scores[t]["กำไรบทบาทนายทุน"] + scores[t]["กำไรบทบาทผู้รับเหมา"]
        
    if len(GAME_DATA) > 0:
        df_sc = pd.DataFrame.from_dict(scores, orient='index').sort_values(by="กำไรสุทธิรวม", ascending=False)
        col_w, col_c = st.columns([1, 1])
        with col_w:
            if df_sc.iloc[0]["กำไรสุทธิรวม"] != 0:
                st.metric(label=f"🏆 ทีมสีที่เป็นผู้นำขณะนี้:", value=f"ทีม {df_sc.index[0]} ({df_sc.iloc[0]['กำไรสุทธิรวม']:,.0f} บาท)")
            st.dataframe(df_sc.style.format("{:,.0f}"))
        with col_c:
            st.bar_chart(df_sc["กำไรสุทธิรวม"])
    else:
        st.info("ยังไม่มีข้อมูลการสรุปบัญชีโครงการ")
