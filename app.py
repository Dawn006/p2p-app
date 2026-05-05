import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json
import gspread
from google.oauth2.service_account import Credentials

# Application Title
st.set_page_config(page_title="P2P Calculator", page_icon="💰")
st.title("💸 P2P USDT Profit & Rate Manager")

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
        
        # ---------------------------------------------------------
        # EXTRA DETAILS FOR EXCEL/SHEETS MATCHING
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
        # SAVE TO GOOGLE SHEETS BUTTON
        # ---------------------------------------------------------
        st.header("💾 မှတ်တမ်းသိမ်းမည် (Save to Google Sheets)")
        if st.button("Save to Google Sheets"):
            try:
                # 1. Google Sheets နှင့် ချိတ်ဆက်ခြင်း
                creds_dict = json.loads(st.secrets["GCP_CREDENTIALS"])
                scopes = [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
                creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
                client = gspread.authorize(creds)
                
                # 2. Google Sheet ကို ဖွင့်ခြင်း (နာမည်အတိအကျဖြစ်ရမည်)
                sheet = client.open("P2P_History").sheet1
                
                # 3. ဒေတာများကို ပုံစံချခြင်း
                current_date = datetime.now().strftime("%d.%m.%Y")
                format_mmk = lambda x: f"{x:,.0f}".replace(",", ".")
                profit_str = f"{profit:,.0f} MMK" if profit > 0 else "0"
                
                # 4. အသစ်ထပ်ထည့်မည့် အကြောင်း (Row)
                row_data = [
                    current_date, 
                    format_mmk(total_mmk), 
                    f"{total_usdt} USDT", 
                    f"{format_mmk(actual_spent)} MMK", 
                    col_e_val, 
                    col_rate_val,
                    exchange_route, 
                    transfer_fee, 
                    f"{transferred_usdt} USDT", 
                    surplus, 
                    leftover_usd, 
                    profit_str
                ]
                
                # 5. Sheet ထဲသို့ ထည့်သွင်းခြင်း
                sheet.append_row(row_data)
                
                st.success("✅ မှတ်တမ်းကို Google Sheets ထဲသို့ အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ! မင်းဖုန်းထဲကနေ ဝင်ကြည့်လို့ရပါပြီ။")
            except Exception as e:
                st.error(f"Error ဖြစ်နေပါသည်။ (Google Sheet နှင့် ချိတ်ဆက်ရန် Secrets များ ထည့်ထားရန် လိုအပ်သည်): {e}")
