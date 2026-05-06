import streamlit as st
import pandas as pd
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="P2P Pro Manager", page_icon="💰", layout="wide")

st.title("💸 P2P USDT Profit & Rate Manager")

# Tabs ခွဲခြင်း
tab1, tab2 = st.tabs(["📥 MMK to USDT (ဝယ်ပေးမယ်)", "📤 USDT to MMK (ပြန်လဲပေးမယ်)"])

# ---------------------------------------------------------
# TAB 1: BUY USDT (MMK to USDT)
# ---------------------------------------------------------
with tab1:
    st.header("Step 1: Basic Calculation")
    total_mmk = st.number_input("Customer ဆီမှ ရရှိသော မြန်မာငွေ (MMK):", min_value=0, step=1000, key="buy_input")
    
    # ရိုက်နေတဲ့အချိန်မှာ တပြိုင်တည်း အဖြတ်အတောက်ပြခြင်း
    if total_mmk > 0:
        st.markdown(f"### 💰 **{total_mmk:,.0f}** MMK")
        
        profit = total_mmk * 0.015
        investable_mmk = total_mmk - profit
        
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"📈 ရရှိမည့် အမြတ် (1.5%): **{profit:,.0f}** MMK")
        with col2:
            st.info(f"💵 USDT ဝယ်ရန် အရင်းငွေ: **{investable_mmk:,.0f}** MMK")
    
    st.divider()
    st.header("Step 2: P2P Buy Results")
    # Table for multiple orders
    initial_data = pd.DataFrame([{"Seller": "", "USDT Amount": 0.0, "MMK Spent": 0}])
    edited_df = st.data_editor(initial_data, num_rows="dynamic", use_container_width=True, key="buy_table")
    
    total_usdt = edited_df["USDT Amount"].sum()
    actual_spent = edited_df["MMK Spent"].sum()
    
    st.write(f"📊 စုစုပေါင်းရရှိသော USDT: **{total_usdt:,.2f}** USDT")
    st.write(f"📉 တကယ်ကုန်ကျသော MMK: **{actual_spent:,.0f}** MMK")

    # ----- အသစ်ထပ်ထည့်ရမည့် "ကျန်ရှိငွေ" အပိုင်း -----
    if total_mmk > 0:
        remaining_mmk = investable_mmk - actual_spent # အရင်းထဲက သုံးလိုက်တာကို နှုတ်မယ်
        
        if remaining_mmk > 0:
            st.info(f"⏳ USDT ဝယ်ရန် ကျန်ရှိသေးသော ငွေ: **{remaining_mmk:,.0f}** MMK")
        elif remaining_mmk == 0 and actual_spent > 0:
            st.success(f"✅ အရင်းငွေ ကွက်တိပြည့်သွားပါပြီ! (ကျန်ငွေ: 0 MMK)")
        elif remaining_mmk < 0:
            st.error(f"⚠️ သတိထားပါ! အရင်းငွေထက် ပိုသုံးနေပါသည်။ (ပိုငွေ: **{abs(remaining_mmk):,.0f}** MMK)")
    # ----------------------------------------------------
    
    if total_usdt > 0:
        customer_rate = total_mmk / total_usdt
        surplus = investable_mmk - actual_spent
        
        st.divider()
        st.header("Step 3: Extra Details (Sheet အတွက်)")
        
        col_e = st.text_input("USDT ခွဲဝယ်မှုများ (Column E):", placeholder="ဥပမာ - 223/34/24")
        col_f = st.text_input("Rate ခွဲဝယ်မှုများ (Column F):", value=f"{customer_rate:,.2f}")
        
        c3, c4, c5 = st.columns(3)
        with c3:
            exchange_route = st.selectbox("Exchange (Column G):", ["Bitget to Binance", "Binance to Binance", "Bitget To Revolute", "Other"])
        with c4:
            transfer_fee = st.number_input("Transfer Fee (USDT - Column H):", min_value=0.0, step=0.001, format="%.3f")
        with c5:
            leftover_usd = st.number_input("Leftover $ (Column K):", min_value=0.0, step=0.01)

        transferred_usdt = total_usdt - transfer_fee

        st.subheader("📤 Summary to Share")
        # ဒီနေရာမှာ Total MMK after fees ကို ထပ်ဖြည့်ထားပါတယ်
        summary = f"SUMMARY\n- Total MMK: {total_mmk:,.0f}\n- Total MMK after fees: {investable_mmk:,.0f}\n- Total USDT: {total_usdt:,.2f}\n- Rate: {customer_rate:,.2f}"
        st.code(summary)

        # SAVE BUTTON
        if st.button("Save to Google Sheets"):
            try:
                creds_dict = json.loads(st.secrets["GCP_CREDENTIALS"])
                scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
                client = gspread.authorize(creds)
                sheet = client.open("P2P_History").sheet1
                
                # Sheet ထဲက Column ၁၂ ခုအတိုင်း စီခြင်း
                row_data = [
                    datetime.now().strftime("%d.%m.%Y"), # A: Date
                    f"{total_mmk:,.0f}",                # B: Customer MMK
                    f"{total_usdt:,.2f} USDT",          # C: Total USDT
                    f"{actual_spent:,.0f} MMK",         # D: Spent MMK
                    col_e,                              # E: USDT ခွဲဝယ်မှုများ
                    col_f,                              # F: Rate ခွဲဝယ်မှုများ
                    exchange_route,                      # G: Exchange
                    transfer_fee,                        # H: Transfer Fee
                    f"{transferred_usdt:,.3f} USDT",     # I: Transferred USDT
                    f"{surplus:,.0f}",                  # J: Surplus
                    leftover_usd,                        # K: Leftover $
                    f"{profit:,.0f} MMK"                # L: Profit
                ]
                
                sheet.append_row(row_data)
                st.success("✅ Google Sheet ထဲသို့ စာရင်းသွင်းပြီးပါပြီ!")
            except Exception as e:
                st.error(f"Error: {e}")

# ---------------------------------------------------------
# TAB 2: SELL USDT (USDT to MMK)
# ---------------------------------------------------------
with tab2:
    st.header("Step 1: Basic Calculation (USDT to MMK)")
    total_usdt_in = st.number_input("Customer ဆီမှ ရရှိသော USDT:", min_value=0.0, step=1.0, format="%.2f", key="sell_input")
    
    if total_usdt_in > 0:
        # ၁.၅% နှုတ်ပြီး P2P မှာ တကယ်ရောင်းမယ့် USDT ကို ရှာမယ်
        profit_usdt = total_usdt_in * 0.015
        sellable_usdt = total_usdt_in - profit_usdt
        
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"📈 ရရှိမည့် အမြတ် (1.5%): **{profit_usdt:,.2f}** USDT")
        with col2:
            st.info(f"💵 P2P တွင် သွားရောင်းရန် အရင်းငွေ: **{sellable_usdt:,.2f}** USDT")

        st.divider()
        st.header("Step 2: P2P Sell Results")
        # P2P မှာ ခွဲရောင်းတဲ့ စာရင်းသွင်းဖို့ ဇယား
        initial_sell_data = pd.DataFrame([{"Buyer": "", "USDT Sold": 0.0, "MMK Received": 0}])
        edited_sell_df = st.data_editor(initial_sell_data, num_rows="dynamic", use_container_width=True, key="sell_table")
        
        actual_usdt_sold = edited_sell_df["USDT Sold"].sum()
        total_mmk_received = edited_sell_df["MMK Received"].sum()
        
        st.write(f"📊 တကယ်ရောင်းလိုက်သော USDT: **{actual_usdt_sold:,.2f}** USDT")
        st.write(f"📉 စုစုပေါင်းရရှိသော MMK: **{total_mmk_received:,.0f}** MMK")

        # ----- ရောင်းရန်ကျန်ရှိသော USDT ကို တွက်ပြမည့်အပိုင်း -----
        remaining_usdt = sellable_usdt - actual_usdt_sold
        
        if remaining_usdt > 0:
            st.info(f"⏳ ရောင်းရန် ကျန်ရှိသေးသော USDT: **{remaining_usdt:,.2f}** USDT")
        elif remaining_usdt == 0 and actual_usdt_sold > 0:
            st.success(f"✅ အရင်း USDT ကွက်တိကုန်သွားပါပြီ!")
        elif remaining_usdt < 0:
            st.error(f"⚠️ သတိထားပါ! အရင်းထက် ပိုရောင်းနေပါသည်။ (ပိုငွေ: **{abs(remaining_usdt):,.2f}** USDT)")
        # ----------------------------------------------------

        if total_mmk_received > 0:
            # Customer ကို ပြမည့် Rate ကို တွက်မယ် (ရလာတဲ့ MMK အားလုံးကို Customer ရဲ့ မူလ USDT နဲ့ စားမယ်)
            customer_rate = total_mmk_received / total_usdt_in
            
            st.divider()
            st.header("Step 3: Extra Details (Sheet အတွက်)")
            
            # ပုံထဲက Column အစဉ်လိုက်အတိုင်း အကွက်များ ဖန်တီးခြင်း
            col_e_sell = st.text_input("USDT ခွဲရောင်းခြင်း (Column E):", placeholder="ဥပမာ - 50/48.5", key="sell_col_e")
            col_f_sell = st.text_input("Rate (Column F):", value=f"{customer_rate:,.2f}", key="sell_col_f")
            
            c3, c4 = st.columns(2)
            with c3:
                exchange_route_sell = st.selectbox("Exchange (Column G):", ["Binance P2P", "Bitget P2P", "Direct", "Other"], key="sell_exch")
                transfer_fee_sell = st.number_input("Transfer Fee (MMK - Column H):", min_value=0, step=100, key="sell_fee")
            with c4:
                surplus_sell = st.number_input("Surplus အပို/အလို (Column J):", value=0, key="sell_surplus")
                leftover_sell = st.number_input("Leftover (Column K):", value=0.0, step=0.1, key="sell_leftover")

            # Customer ဆီ တကယ်လွှဲပေးရမယ့်ငွေ (ရလာတဲ့ MMK အားလုံးထဲကမှ လွှဲခကို နုတ်မယ်)
            transferred_mmk = total_mmk_received - transfer_fee_sell

            st.subheader("📤 Summary to Share")
            sell_summary = f"SUMMARY\n- Total USDT: {total_usdt_in:,.2f}\n- Total MMK to Pay: {transferred_mmk:,.0f}\n- Rate: {customer_rate:,.2f}"
            st.code(sell_summary)
            
            # --- GOOGLE SHEETS သိမ်းမည့် အပိုင်း ---
            if st.button("Save to Google Sheets", key="sell_save_btn"):
                try:
                    creds_dict = json.loads(st.secrets["GCP_CREDENTIALS"])
                    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
                    client = gspread.authorize(creds)
                    
                    sheet_sell = client.open("P2P_Sell_History").sheet1 
                    
                    # Sheet ထဲက Column ၁၂ ခုအတိုင်း ကွက်တိစီခြင်း
                    row_data = [
                        datetime.now().strftime("%d.%m.%Y"),   # A: Date
                        f"{total_usdt_in:,.2f} USDT",          # B: Customer USDT
                        f"{total_mmk_received:,.0f} MMK",      # C: Total MMK
                        f"{actual_usdt_sold:,.2f} USDT",       # D: Spent USDT
                        col_e_sell,                            # E: USDT ခွဲရောင်းခြင်း
                        col_f_sell,                            # F: Rate
                        exchange_route_sell,                   # G: Exchange
                        f"{transfer_fee_sell:,.0f}",           # H: Transfer fee (MMK)
                        f"{transferred_mmk:,.0f} MMK",         # I: Transferred MMK
                        f"{surplus_sell:,.0f}",                # J: Surplus
                        f"{leftover_sell:,.2f}",               # K: Leftover
                        f"{profit_usdt:,.2f} USDT"             # L: Profit
                    ]
                    
                    sheet_sell.append_row(row_data)
                    st.success("✅ Sell Record ကို Google Sheet ထဲ အောင်မြင်စွာ သိမ်းပြီးပါပြီ!")
                except Exception as e:
                    st.error(f"Error: {e}")
