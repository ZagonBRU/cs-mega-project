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

# โหลดฐานข้อมูลทั้งหมดเข้าสู่ระบบ
TEAMS = load_json(TEAM_FILE, ["แดง 1", "แดง 2", "เหลือง 1", "เหลือง 2", "เขียว 1", "เขียว 2", "ฟ้า 1", "ฟ้า 2"])
MATERIAL_PRICES = load_json(ITEM_FILE, {"ไม้เสียบลูกชิ้น *": 2000, "ตะเกียบ *": 4000, "กระดาษ A4": 2000})
PROJECT_MASTER = load_json(PROJECT_FILE, {})
GAME_DATA = load_json(DATA_FILE, [])

# ประมวลผลหา "สถานะปัจจุบัน" ของโปรเจกต์แต่ละเลเวลแบบ Dynamic
STATUS_MAP = {}
for deal in GAME_DATA:
    key = f"{deal['project_id']}-{deal['difficulty']}"
    if deal["result"] == "ผ่าน":
        STATUS_MAP[key] = "เสร็จสิ้น"
    elif deal["result"] == "รอตรวจ" and STATUS_MAP.get(key) != "เสร็จสิ้น":
        STATUS_MAP[key] = "กำลังดำเนินการ"
    elif deal["result"] in ["ไม่ผ่าน", "ยกเลิก"] and STATUS_MAP.get(key) not in ["กำลังดำเนินการ", "เสร็จสิ้น"]:
        STATUS_MAP[key] = "ว่าง"

# 🧭 เมนูการจัดหน้าสตรีมลิต
tab1, tab2, tab3 = st.tabs(["🌐 คู่มือและบอร์ดสถานะโครงการ (สำหรับนักศึกษา)", "🔐 ระบบควบคุมเกม (Staff Only)", "🏆 สรุปคะแนนลีดเดอร์บอร์ด"])

# ==========================================
# 🌐 TAB 1: คู่มือดิจิทัล & บอร์ดแสดงสถานะสาธารณะ
# ==========================================
with tab1:
    st.header("📋 คู่มือภารกิจเมกะโปรเจกต์ & เช็กสถานะงานดิจิทัล")
    st.caption("นักศึกษาสามารถสแกนเข้ามาอ่านรายละเอียดเงื่อนไขและจองงานได้จากหน้านี้โดยไม่ต้องใช้กระดาษ")
    
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
        # ---------------------------------------------------------
        # ส่วนที่ 1: ลงทะเบียนโครงการ + สั่งซื้อวัสดุ (ฝั่งซ้าย)
        # ---------------------------------------------------------
        st.subheader("📝 1. ส่วนลงทะเบียนโครงการ & บันทึกบิลซื้อวัสดุ")
        col_f, col_edit = st.columns([1, 1.2])
        
        with col_f:
            st.markdown("##### 📥 ฟอร์มลงทะเบียนและสั่งของใหม่")
            deal_choices = []
            for pid, pdata in PROJECT_MASTER.items():
                for lvl in pdata["levels"].keys():
                    key = f"{pid}-{lvl}"
                    if STATUS_MAP.get(key) != "เสร็จสิ้น":
                        deal_choices.append(key)
            
            if deal_choices:
                chosen_key = st.selectbox("เลือกโครงการ (รหัสโครงการ-ระดับ):", sorted(deal_choices), 
                                          format_func=lambda x: f"งาน {x.split('-')[0]} {PROJECT_MASTER[x.split('-')[0]]['name']} (ระดับ {x.split('-')[1]})", key="new_deal_box")
                p_id, d_lvl = chosen_key.split("-")
                reward_amt = PROJECT_MASTER[p_id]["levels"][d_lvl]["reward"]
                
                st.markdown(f"💰 **มูลค่าสัญญาโครงการ:** `{reward_amt:,}` บาท")
                investor = st.selectbox("ทีมนักลงทุน:", TEAMS, index=0, key="new_inv")
                inv_pct = st.number_input("สัดส่วนแบ่งกำไรฝั่งนักลงทุน %", min_value=0, max_value=100, value=60, key="new_inv_pct")
                contractor = st.selectbox("ทีมผู้รับเหมา:", TEAMS, index=1, key="new_con")
                budget = st.number_input("งบประมาณที่ตกลงกันไว้ (บาท):", min_value=0, value=200000, key="new_budget")
                
                # ตารางเปิดบิลวัสดุ (คิดเงินรวมเฉลี่ย ไม่ต้องบันทึกไอเทมแยก)
                mat_cost_calc = 0
                with st.expander("🛒 เปิดบิลคำนวณราคาวัสดุ (สั่งซื้อได้ครั้งเดียว)", expanded=False):
                    for mat, price in MATERIAL_PRICES.items():
                        qty = st.number_input(f"{mat} ({price:,} บ.)", min_value=0, value=0, key=f"order_{mat}")
                        mat_cost_calc += qty * price
                st.markdown(f"📦 **ราคารวมวัสดุสั่งซื้อ:** `{mat_cost_calc:,}` บาท")
                
                if st.button("📥 ยืนยันการลงทะเบียนโครงการ", use_container_width=True):
                    if investor == contractor: 
                        st.error("❌ ห้ามนักลงทุนและผู้รับเหมาเป็นทีมเดียวกันครับ")
                    else:
                        GAME_DATA.append({
                            "project_id": p_id, "project_name": PROJECT_MASTER[p_id]["name"],
                            "difficulty": int(d_lvl), "reward": reward_amt, "investor": investor,
                            "investor_pct": inv_pct, "contractor": contractor, "contractor_pct": 100 - inv_pct,
                            "budget": budget, "material_cost": mat_cost_calc, "times": 0, "result": "รอตรวจ", "net_profit": 0
                        })
                        save_json(DATA_FILE, GAME_DATA)
                        st.success("✅ บันทึกข้อมูลลงทะเบียนสำเร็จ!")
                        st.rerun()
            else:
                st.info("โครงการทุกระดับถูกทำเสร็จสิ้นหมดแล้ว!")

        # ---------------------------------------------------------
        # ส่วนที่ 2: แสดงตารางภาพรวมโครงการ และระบบแก้ไข/ยกเลิก (ฝั่งขวา)
        # ---------------------------------------------------------
        with col_edit:
            st.markdown("##### 📊 ตารางภาพรวมและระบบแก้ไขข้อมูล / ขอยกเลิก")
            if GAME_DATA:
                df_overview = pd.DataFrame(GAME_DATA)
                display_cols = ["project_id", "difficulty", "investor", "contractor", "material_cost", "budget", "result"]
                df_display = df_overview[display_cols].copy()
                df_display.columns = ["รหัส", "ระดับ", "นักลงทุน", "ผู้รับเหมา", "ค่าวัสดุ", "งบลงทุน", "ผลการตรวจ"]
                
                # เครื่องมือเลือก Row จากตารางเพื่อนำมาแก้ไขข้อมูลที่ผิดพลาด
                selected_row_idx = st.selectbox("🎯 เลือกแถวคิวงานที่ต้องการ แก้ไขข้อมูล / ขอยกเลิก:", range(len(GAME_DATA)), 
                                                 format_func=lambda x: f"คิวที่ {x} | โพรเจกต์ {GAME_DATA[x]['project_id']} (ระดับ {GAME_DATA[x]['difficulty']}) -> ทีม {GAME_DATA[x]['contractor']}")
                
                target_edit = GAME_DATA[selected_row_idx]
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    with st.expander("✏️ คลิกเพื่อแก้ไขกรณีลงทะเบียนผิด"):
                        edit_inv = st.selectbox("แก้ไขนักลงทุน:", TEAMS, index=TEAMS.index(target_edit["investor"]), key=f"ed_inv_{selected_row_idx}")
                        edit_pct = st.number_input("แก้ไขสัดส่วน %:", min_value=0, max_value=100, value=int(target_edit["investor_pct"]), key=f"ed_pct_{selected_row_idx}")
                        edit_con = st.selectbox("แก้ไขผู้รับเหมา:", TEAMS, index=TEAMS.index(target_edit["contractor"]), key=f"ed_con_{selected_row_idx}")
                        edit_bug = st.number_input("แก้ไขงบลงทุน:", min_value=0, value=int(target_edit["budget"]), key=f"ed_bug_{selected_row_idx}")
                        edit_mat = st.number_input("แก้ไขราคารวมวัสดุ:", min_value=0, value=int(target_edit["material_cost"]), key=f"ed_mat_{selected_row_idx}")
                        
                        if st.button("💾 บันทึกการแก้ไข", key=f"btn_save_ed_{selected_row_idx}"):
                            GAME_DATA[selected_row_idx].update({"investor": edit_inv, "investor_pct": edit_pct, "contractor": edit_con, "contractor_pct": 100 - edit_pct, "budget": edit_bug, "material_cost": edit_mat})
                            save_json(DATA_FILE, GAME_DATA)
                            st.success("แก้ไขข้อมูลเรียบร้อย!")
                            st.rerun()
                            
                with col_btn2:
                    if target_edit["result"] == "รอตรวจ":
                        if st.button("🚨 ขอยกเลิกโครงการนี้", type="primary", key=f"btn_cancel_{selected_row_idx}", use_container_width=True):
                            # กฎเหล็ก: ผู้รับเหมาไม่เสียเงิน แต่นายทุนเสียเงินลงทุนก้อนแรกทันที (net_profit = -budget)
                            GAME_DATA[selected_row_idx]["result"] = "ยกเลิก"
                            GAME_DATA[selected_row_idx]["net_profit"] = -int(target_edit["budget"])
                            save_json(DATA_FILE, GAME_DATA)
                            st.warning("⚠️ ยกเลิกโครงการแล้ว (ทีมนายทุนสูญเสียเงินลงทุนก้อนแรกเรียบร้อย)")
                            st.rerun()
                st.dataframe(df_display, use_container_width=True)
            else:
                st.info("ยังไม่มีข้อมูลลงทะเบียนในระบบ")

        # ---------------------------------------------------------
        # ส่วนที่ 3: ⏱️ บันทึกผลการตรวจงาน (ด้านล่างสุด)
        # ---------------------------------------------------------
        st.markdown("---")
        st.subheader("⏱️ 2. ส่วนบันทึกผลการตรวจงาน")
        
        # กรองดึงเฉพาะรายการโครงการทั้งหมดที่ "กำลังดำเนินการ" อยู่ (สถานะผลตรวจเป็น 'รอตรวจ' หรือ 'ไม่ผ่าน')
        pending_indices = [idx for idx, r in enumerate(GAME_DATA) if r["result"] in ["รอตรวจ", "ไม่ผ่าน"]]
        
        if pending_indices:
            df_pending = pd.DataFrame([GAME_DATA[i] for i in pending_indices])[["project_id", "difficulty", "investor", "contractor", "material_cost", "budget"]]
            df_pending.columns = ["รหัสโครงการ", "ระดับความยาก", "ทีมนักลงทุน", "ทีมผู้รับเหมา", "ราคารวมวัสดุเดิม", "งบประมาณโครงการ"]
            st.markdown("*ตารางโครงการที่กำลังดำเนินการอยู่ทั้งหมด หน้างานจะส่งตรวจกี่ครั้งก็ได้จนกว่าจะผ่าน:*")
            st.dataframe(df_pending, use_container_width=True, hide_index=True)
            
            # คลิก Row ตรวจสอบสถานะงานผ่าน Dropdown Selector Index
            audit_idx = st.selectbox("🔍 คลิกเลือกโครงการที่กำลังดำเนินการอยู่เพื่อบันทึกผลการตรวจงาน:", pending_indices,
                                     format_func=lambda x: f"โพรเจกต์ {GAME_DATA[x]['project_id']} (ระดับ {GAME_DATA[x]['difficulty']}) -> ผู้รับเหมา: {GAME_DATA[x]['contractor']}")
            
            target_audit = GAME_DATA[audit_idx]
            
            # 💰 ระบบคำนวณยอดเงินคงเหลือเพื่อเตรียมหักค่าตรวจ 2,000 บาท
            # เงินคงเหลือคำนวณจาก: งบประมาณลงทุน - ค่าวัสดุ - (จำนวนครั้งที่เคยตรวจ * 2000)
            previous_audit_fee = int(target_audit.get("times", 0)) * 2000
            current_balance = int(target_audit["budget"]) - int(target_audit["material_cost"]) - previous_audit_fee
            
            st.markdown(f"💳 **ตรวจสอบสถานะบัญชีหน้างาน:**")
            st.markdown(f"- งบประมาณก้อนลงทุน: `{target_audit['budget']:,}` บาท | - หักราคาค่าของที่สั่งไปแล้ว: `{target_audit['material_cost']:,}` บาท")
            st.markdown(f"- เคยส่งตรวจมาแล้ว: `{target_audit['times']}` ครั้ง (หักเงินสะสมไปแล้ว `{previous_audit_fee:,}` บาท)")
            st.error(f"💰 ยอดเงินทุนคงเหลือของโครงการปัจจุบัน: **{current_balance:,}** บาท (ระบบเตรียมตัดสิทธิ์หักค่าตรวจรอบนี้อีก **2,000** บาท)")
            
            # ฟอร์มบันทึกครั้งที่ตรวจและผลลัพธ์
            col_au1, col_au2 = st.columns(2)
            with col_au1:
                next_time_count = int(target_audit.get("times", 0)) + 1
                st.number_input("ครั้งที่ตรวจระบบจะรันให้อัตโนมัติ:", value=next_time_count, disabled=True, key="display_times")
            with col_au2:
                eval_result = st.selectbox("ผลลัพธ์การตรวจสอบรอบนี้:", ["ผ่าน", "ไม่ผ่าน"], key="eval_result_box")
                
            if st.button("💾 ยืนยันการบันทึกผลการตรวจงานรอบนี้", type="primary"):
                # ทำการหักค่าตรวจเพิ่มในระบบและจำจำนวนครั้งสะสม
                GAME_DATA[audit_idx]["times"] = next_time_count
                total_spent = int(target_audit["material_cost"]) + (next_time_count * 2000)
                
                if eval_result == "ผ่าน":
                    GAME_DATA[audit_idx]["result"] = "ผ่าน"
                    # คำนวณกำไรสุทธิรวม: (เงินรางวัล - เงินทุนค่าวัสดุและค่าตรวจทั้งหมด)
                    GAME_DATA[audit_idx]["net_profit"] = int(target_audit["reward"]) - total_spent
                    st.success(f"🎉 ยินดีด้วย! โครงการเปลี่ยนสถานะเป็น [เสร็จสิ้น] และล็อกระบบระดับความยากนี้เรียบร้อยแล้ว")
                else:
                    GAME_DATA[audit_idx]["result"] = "ไม่ผ่าน"
                    # หากไม่ผ่าน โครงการยังคงค้างอยู่ในระบบ ดำเนินการต่อเพื่อส่งตรวจใหม่รอบหน้าได้ เงินปันผลยังไม่คิดจนกว่าจะผ่านหรือขอยกเลิก
                    st.warning(f"❌ ผลการตรวจคิวนี้คือ [ไม่ผ่าน] โครงการยังคงดำเนินการต่อไปเพื่อแก้ไขและส่งตรวจใหม่ครั้งถัดไป")
                    
                save_json(DATA_FILE, GAME_DATA)
                st.rerun()
        else:
            st.info("🎉 ไม่มีโครงการที่กำลังดำเนินการ (กำลังรอตรวจ) ในระบบขณะนี้")

        # 💾 ระบบสำรองข้อมูลหน้างานกันหาย (Backup & Restore)
        st.markdown("---")
        st.subheader("💾 ระบบรักษาความปลอดภัยข้อมูล (กันระบบคลาวด์หลับ)")
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
                    st.success("✅ กู้คืนระบบสำเร็จ!")
                    st.rerun()

# ==========================================
# 🏆 TAB 3: LEADERBOARD & SUMMARY
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
                # ถ้ายกเลิก นายทุนรับความเสี่ยงยอดติดลบตามงบก้อนแรก ผู้รับเหมาได้ 0 (ไม่เจ็บตัว)
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
