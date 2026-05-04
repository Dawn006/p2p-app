import streamlit as st
import pandas as pd
import os
from datetime import datetime
import requests

# Application Title
st.set_page_config(page_title="P2P Calculator", page_icon="💰")
st.title("💸 P2P USDT Profit & Rate Manager")

# ---------------------------------------------------------
# NEW FEATURE: LIVE BINANCE P2P RATE
# ---------------------------------------------------------
st.header("📊 Live Binance P2P Rate (MMK/USDT)")

if st.button("Live Rate ကြည့်မည်"):
    try:
        # Binance ဆီကို လှမ်းတောင်းမည့် လိပ်စာ (API endpoint)
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        
        # လုံခြုံရေးတံခါးကို ဖြတ်ဖို့ (လူအစစ်ပါလို့ ဟန်ဆောင်ခြင်း)
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Length": "123",
            "content-type": "application/json",
            "Host": "p2p.binance.com",
            "Origin": "https://p2p.binance.com",
            "Pragma": "no-cache",
            "TE": "Trailers",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        }
        
        # ငါတို့ လိုချင်တဲ့ အချက်အလက် (USDT ကို MMK နဲ့ ဝယ်မယ်)
        data = {
            "asset": "USDT",
            "fiat": "MMK",
            "tradeType": "BUY",
            "page": 1,
            "rows": 5,
            "payTypes": [],
            "publisherType": None
        }
        
        # requests ကို သုံးပြီး သွားမေးခြင်း
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        

        # ရလာတဲ့ ဒေတာတွေကို ဖော်ပြခြင်း
        if result['code'] == '000000':
            sellers = result['data']
            
            if len(sellers) > 0:
                st.success("✅ လက်ရှိ ပေါက်ဈေးများ ရရှိပါပြီ!")
                for index, seller in enumerate(sellers):
                    price = seller['adv']['price']
                    name = seller['advertiser']['nickName']
                    st.write(f"{index + 1}. **{name}** : `{price}` MMK")
            else:
                st.warning("⚠️ Binance နှင့် ချိတ်ဆက်မိသော်လည်း လောလောဆယ် ဈေးတင်ထားသူ မတွေ့ပါ။")
        else:
            st.error("Rate ယူရာတွင် အခက်အခဲရှိနေပါသည်။")
            
    except Exception as e:
        st.warning(f"Connection Error: လောလောဆယ် လှမ်းယူ၍ မရပါ။ (Binance မှ ပိတ်ထားနိုင်ပါသည်) {e}")

st.divider()

# Step 1: Input from Customer
st.header("Step 1: Basic Calculation")
total_mmk = st.number_input("Customer ဆီမှ ရရှိသော မြန်မာငွေ (MMK):", min_value=0, step=1000)

if total_mmk > 0:
    # 1.5% Profit Logic
    profit = total_mmk * 0.015
    investable_mmk = total_mmk - profit
    
    st.success(f"📈 **ရရှိမည့် အမြတ် (1.5%):** {profit:,.0f} MMK")
    st.info(f"💵 **USDT ဝယ်ရန် အရင်းငွေ:** {investable_mmk:,.0f} MMK")
    
    st.divider()

    # Step 2: Input Multiple P2P Screenshots
    st.header("Step 2: P2P Buy Results (Multiple Orders)")
    st.write("ဝယ်ယူခဲ့သော Seller တစ်ယောက်ချင်းစီအတွက် အောက်ပါဇယားတွင် အချက်အလက်များ ထည့်ပါ။ (ဇယားအောက်ခြေရှိ အပေါင်းလက္ခဏာကို နှိပ်၍ အကွက်အသစ် ထပ်တိုးနိုင်ပါသည်။)")
    
    # Create an empty, editable table
    initial_data = pd.DataFrame(
        [{"Seller/မှတ်စု": "", "USDT Amount": 0.0, "MMK Spent": 0}]
    )
    
    edited_df = st.data_editor(initial_data, num_rows="dynamic", use_container_width=True)
    
    # Automatically sum the columns
    total_usdt = edited_df["USDT Amount"].sum()
    actual_spent = edited_df["MMK Spent"].sum()
    
    # Show real-time totals below the table
    st.markdown(f"**📊 စုစုပေါင်း ဝယ်ယူရရှိသော USDT:** `{total_usdt:,.2f}` USDT")
    st.markdown(f"**📉 တကယ်ကုန်ကျခဲ့သော MMK:** `{actual_spent:,.0f}` MMK")
        
    if total_usdt > 0:
        # Hide profit inside the rate
        customer_rate = total_mmk / total_usdt
        surplus = investable_mmk - actual_spent
        
        st.divider()
        
        # FINAL OUTPUT
        st.header("📋 Final Summary")
        
        # Shareable part
        st.subheader("📤 မိတ်ဆွေထံသို့ ပို့ရန်စာ")
        summary_text = f"""SUMMARY 

- Total MMK: {total_mmk:,.0f}
- Total MMK after fees: {investable_mmk:,.0f}
- Total USDT: {total_usdt:,.2f}
- Rate: {customer_rate:,.2f}"""
        st.code(summary_text)
        
        # Internal part
        st.subheader("🔒 ကိုယ့်အတွက် စာရင်း")
        st.write(f"- အိတ်ကပ်ထဲကျန်မည့် အမြတ်: **{profit:,.0f} MMK**")
        st.write(f"- အကြွေပို/လို: **{surplus:,.0f} MMK**")
        
        st.divider()
        
        # ---------------------------------------------------------
        # EXTRA DETAILS FOR EXCEL MATCHING
        # ---------------------------------------------------------
        st.divider()
        st.header("📝 Excel အတွက် အပိုအချက်အလက်များ")
        
        col_e_val = st.text_input("USDT ခွဲဝယ်မှုများ (Column E အတွက် / ဥပမာ - 223.31/.21/189.75):", "")
        col_rate_val = st.text_input("Rate ခွဲဝယ်မှုများ (ဥပမာ - 4478/80/98):", str(round(customer_rate, 2)))
        
        col3, col4 = st.columns(2)
        with col3:
            exchange_route = st.selectbox("Exc (လွှဲပြောင်းမှုပုံစံ):", ["Bitget to Binance", "Binance to Binance", "Bitget To Revolute", "Other"])
            transfer_fee = st.number_input("Transfer Fee (USDT):", min_value=0.0, step=0.01, format="%.3f")
        with col4:
            leftover_usd = st.number_input("Leftover $:", min_value=0, step=1)
            
        # တွက်ချက်မှုအသစ် (Transferred USDT = Total - Fee)
        transferred_usdt = total_usdt - transfer_fee

        # ---------------------------------------------------------
        # SAVE TO HISTORY BUTTON (EXACT EXCEL FORMAT)
        # ---------------------------------------------------------
        st.header("💾 မှတ်တမ်းသိမ်းမည် (Save History)")
        if st.button("Save to History (CSV သို့ သိမ်းရန်)"):
            # ပုံထဲကအတိုင်း 26.3.2026 ပုံစံ Date ပြောင်းခြင်း
            current_date = datetime.now().strftime("%d.%m.%Y")
            
            # ဂဏန်းများကို 2.373.250 ပုံစံဖြစ်အောင် ကော်မာအစား အစက်(.) ပြောင်းခြင်း
            format_mmk = lambda x: f"{x:,.0f}".replace(",", ".")
            
            # Prepare the row matching your exact screenshot headers
            new_record = pd.DataFrame([{
                "Date": current_date,
                "Transfer MMK": format_mmk(total_mmk),
                "USDT": f"{total_usdt} USDT",
                "MMK": f"{format_mmk(actual_spent)} MMK",
                " ": col_e_val,  # ခေါင်းစဉ်မပါတဲ့ Column E အတွက်
                "Rate": col_rate_val,
                "Exc": exchange_route,
                "Transfer Fee": transfer_fee,
                "Transferred USDT": f"{transferred_usdt} USDT",
                "Leftover MMK": surplus,
                "Leftover $": leftover_usd,
                "Profit": f"{profit:,.0f} MMK" if profit > 0 else "0"
            }])
            
            file_name = "p2p_history_exact.csv"
            
            if os.path.exists(file_name):
                new_record.to_csv(file_name, mode='a', header=False, index=False)
            else:
                new_record.to_csv(file_name, mode='w', header=True, index=False)
                
            st.success("✅ မှတ်တမ်းကို **p2p_history_exact.csv** ဖိုင်ထဲသို့ ပုံစံအတိုင်း အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ!")
