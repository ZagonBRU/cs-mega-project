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
TEAMS = load_json(TEAM_FILE, [])
MATERIAL_PRICES = load_json(ITEM_FILE, {})
PROJECT_MASTER = load_json(PROJECT_FILE, {})
GAME_DATA = load_json(DATA_FILE, [])

# ประมวลผลหา "สถานะปัจจุบัน" ของโปรเจกต์แต่ละเลเวลแบบ Dynamic
STATUS_MAP = {}
for deal in GAME_DATA:
    key = f"{deal['project_id']}-{deal['difficulty']}"
    if deal["result"] == "ผ่าน":
        STATUS_MAP[key] = "สำเร็จ"
    elif deal["result"] == "รอตรวจ" and STATUS_MAP.get(key) != "สำเร็จ":
        STATUS_MAP[key] = "กำลังดำเนินการ"

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
        
        st.markdown("**📊 สถานะการจองในแต่ละระดับความยาก:**")
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
    else:
        st.error("ไม่พบไฟล์ Project_List.json กรุณาตรวจสอบการวางไฟล์")

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
        col_f, col_t = st.columns([1, 2])
        
        # ฝั่งซ้าย: คีย์ใบจดทะเบียนดีลงานใหม่
        with col_f:
            st.subheader("📝 ออกใบจดทะเบียนดีลใหม่")
            deal_choices = []
            for pid, pdata in PROJECT_MASTER.items():
                for lvl in pdata["levels"].keys():
                    key = f"{pid}-{lvl}"
                    if STATUS_MAP.get(key) != "สำเร็จ":
                        deal_choices.append(key)
            
            if deal_choices:
                chosen_key = st.selectbox("เลือกงาน (รหัสโครงการ-ระดับ):", sorted(deal_choices), 
                                          format_func=lambda x: f"งาน {x.split('-')[0]} {PROJECT_MASTER[x.split('-')[0]]['name']} (ระดับ {x.split('-')[1]})")
                p_id, d_lvl = chosen_key.split("-")
                reward_amt = PROJECT_MASTER[p_id]["levels"][d_lvl]["reward"]
                
                st.warning(f"💰 รางวัลของสัญญาข้อนี้: {reward_amt:,} บาท")
                investor = st.selectbox("ทีมนักลงทุน:", TEAMS, index=0)
                inv_pct = st.number_input("สัดส่วนนักลงทุน %", min_value=0, max_value=100, value=60)
                contractor = st.selectbox("ทีมผู้รับเหมา:", TEAMS, index=1)
                budget = st.number_input("งบประมาณลงทุน (บาท):", min_value=0, value=200000)
                
                if st.button("📥 บันทึกสัญญาลงระบบ"):
                    if investor == contractor: st.error("❌ ห้ามนักลงทุนและผู้รับเหมาเป็นทีมเดียวกันครับ")
                    else:
                        GAME_DATA.append({
                            "project_id": p_id, "project_name": PROJECT_MASTER[p_id]["name"],
                            "difficulty": int(d_lvl), "reward": reward_amt, "investor": investor,
                            "investor_pct": inv_pct, "contractor": contractor, "contractor_pct": 100 - inv_pct,
                            "budget": budget, "material_cost": 0, "times": "-", "result": "รอตรวจ", "net_profit": 0
                        })
                        save_json(DATA_FILE, GAME_DATA)
                        st.success("บันทึกใบลงทะเบียนเรียบร้อย!")
                        st.rerun()
            else:
                st.info("โครงการทุกระดับถูกทำสำเร็จครบถ้วนหมดแล้ว!")
                    
        # ฝั่งขวา: ตารางคิวงานหลังบ้านและการบันทึกผลการประเมิน
        with col_t:
            st.subheader("📊 รายการควบคุมและตรวจประเมินผล")
            if len(GAME_DATA) > 0:
                st.dataframe(pd.DataFrame(GAME_DATA).drop(columns=["material_cost", "investor_pct", "contractor_pct"]), use_container_width=True)
                
                pending = [f"คิวที่ {idx} | โครงการ {r['project_id']} -> ทีม {r['contractor']}" for idx, r in enumerate(GAME_DATA) if r["result"] == "รอตรวจ"]
                if pending:
                    sel_job = st.selectbox("เลือกงานค้างตรวจเพื่อบันทึกผล:", pending)
                    t_idx = int(sel_job.split(" ")[2])
                    
                    st.markdown("**🛒 คำนวณราคาวัสดุร้านค้ากลาง**")
                    cost_calc = 0
                    with st.expander("เปิดบิลวัสดุที่ใช้จริง"):
                        for mat, price in MATERIAL_PRICES.items():
                            qty = st.number_input(f"{mat} ({price:,} บ.)", min_value=0, value=0, key=f"m_{t_idx}_{mat}")
                            cost_calc += qty * price
                        times = st.number_input("ครั้งที่เข้าตรวจตรวจงาน", min_value=1, value=1, key=f"t_{t_idx}")
                        cost_calc += (times * 2000)
                        st.markdown(f"**รวมค่าวัสดุ + ค่าตรวจงาน: {cost_calc:,} บาท**")
                        
                    f_cost = st.number_input("ยืนยันค่ายอดวัสดุสุทธิ (บาท)", min_value=0, value=cost_calc)
                    res = st.selectbox("ผลการประเมินโครงการ:", ["ผ่าน", "ยกเลิก"])
                    
                    if st.button("💾 ยืนยันผลการตรวจ"):
                        GAME_DATA[t_idx]["times"] = times
                        GAME_DATA[t_idx]["material_cost"] = f_cost
                        GAME_DATA[t_idx]["result"] = res
                        GAME_DATA[t_idx]["net_profit"] = (GAME_DATA[t_idx]["reward"] - f_cost) if res == "ผ่าน" else -f_cost
                        save_json(DATA_FILE, GAME_DATA)
                        st.success("อัปเดตระบบบัญชีเรียบร้อย")
                        st.rerun()
                else:
                    st.info("🎉 ไม่มีโครงการค้างตรวจในขณะนี้")
            else:
                st.info("ยังไม่มีข้อมูลใบลงทะเบียนเข้ามา")

        # 💾 ==========================================
        # ระบบสำรองข้อมูลหน้างานกันหาย (Backup & Restore)
        # ==========================================
        st.markdown("---")
        st.subheader("💾 ระบบรักษาความปลอดภัยข้อมูล (กันระบบคลาวด์หลับ)")
        col_bk1, col_bk2 = st.columns(2)
        
        with col_bk1:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                current_data_str = f.read()
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์สำรองข้อมูลล่าสุด (Backup)",
                data=current_data_str,
                file_name="Mega_Project_Backup.json",
                mime="application/json"
            )
            st.caption("💡 แนะนำให้สตาฟกดดาวน์โหลดเก็บไว้ในคอมฯ ทุกๆ 20-30 นาที")
            
        with col_bk2:
            uploaded_backup = st.file_uploader("📂 กู้คืนสถานะคะแนนและดีล (Restore)", type=["json"])
            if uploaded_backup is not None:
                if st.button("🔄 ยืนยันคำสั่งกู้คืนระบบ"):
                    try:
                        backup_data = json.load(uploaded_backup)
                        save_json(DATA_FILE, backup_data)
                        st.success("✅ กู้คืนระบบบัญชีหน้างานและคะแนนสะสมสำเร็จ!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาดในการโหลดไฟล์สำรอง: {e}")

# ==========================================
# 🏆 TAB 3: LEADERBOARD & SUMMARY
# ==========================================
with tab3:
    st.header("🏆 อันดับคะแนนลีดเดอร์บอร์ดสดหน้างาน")
    scores = {t: {"กำไรบทบาทนายทุน": 0, "กำไรบทบาทผู้รับเหมา": 0, "กำไรสุทธิรวม": 0} for t in TEAMS}
    for d in GAME_DATA:
        if d["result"] != "รอตรวจ":
            if d["result"] == "ผ่าน":
                scores[d["investor"]]["กำไรบทบาทนายทุน"] += d["net_profit"] * (d["investor_pct"]/100)
                scores[d["contractor"]]["กำไรบทบาทผู้รับเหมา"] += d["net_profit"] * (d["contractor_pct"]/100)
            else:
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
