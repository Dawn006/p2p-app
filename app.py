import streamlit as st
import pandas as pd
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="P2P Pro Manager", page_icon="💰", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stNumberInput div div input { font-size: 18px !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("💸 P2P USDT Profit & Rate Manager")

# Create Tabs for Buy and Sell
tab1, tab2 = st.tabs(["📥 MMK to USDT (ဝယ်ပေးမယ်)", "📤 USDT to MMK (ပြန်လဲပေးမယ်)"])

# ---------------------------------------------------------
# TAB 1: MMK to USDT (Buy USDT for Customer)
# ---------------------------------------------------------
with tab1:
    st.header("Step 1: Receive MMK from Customer")
    total_mmk = st.number_input("လက်ခံရရှိသော မြန်မာငွေ (MMK):", min_value=0, step=1000, format="%d", key="buy_mmk")
    
    # Comma formatted display for input confirmation
    if total_mmk > 0:
        st.write(f"💰 ရိုက်ထည့်လိုက်သောပမာဏ: **{total_mmk:,.0f}** MMK")
        
        profit_mmk = total_mmk * 0.015
        investable_mmk = total_mmk - profit_mmk
        
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"📈 အမြတ် (1.5%): **{profit_mmk:,.0f}** MMK")
        with col2:
            st.info(f"💵 အရင်းငွေ: **{investable_mmk:,.0f}** MMK")

        st.divider()
        st.header("Step 2: P2P Buy Orders")
        initial_buy_data = pd.DataFrame([{"Seller": "", "USDT": 0.0, "MMK Spent": 0}])
        edited_buy_df = st.data_editor(initial_buy_data, num_rows="dynamic", use_container_width=True, key="buy_table")
        
        total_usdt_bought = edited_buy_df["USDT"].sum()
        actual_spent_mmk = edited_buy_df["MMK Spent"].sum()
        
        if total_usdt_bought > 0:
            customer_rate = total_mmk / total_usdt_bought
            surplus = investable_mmk - actual_spent_mmk
            
            st.subheader("📋 Final Summary (Buy)")
            sum_text = f"SUMMARY\n- Total MMK: {total_mmk:,.0f}\n- Total USDT: {total_usdt_bought:,.2f}\n- Rate: {customer_rate:,.2f}"
            st.code(sum_text)
            st.write(f"🔒 အိတ်ကပ်ထဲကျန်မည့်အမြတ်: **{profit_mmk:,.0f}** MMK")
            st.write(f"⚖️ အကြွေ ပို/လို: **{surplus:,.0f}** MMK")

# ---------------------------------------------------------
# TAB 2: USDT to MMK (Sell USDT for Customer)
# ---------------------------------------------------------
with tab2:
    st.header("Step 1: Receive USDT from Customer")
    total_usdt_in = st.number_input("လက်ခံရရှိသော USDT:", min_value=0.0, step=1.0, format="%.2f", key="sell_usdt")
    
    if total_usdt_in > 0:
        profit_usdt = total_usdt_in * 0.015
        sellable_usdt = total_usdt_in - profit_usdt
        
        col3, col4 = st.columns(2)
        with col3:
            st.success(f"📈 အမြတ် (1.5%): **{profit_usdt:,.2f}** USDT")
        with col4:
            st.warning(f"💵 P2P မှာပြန်ရောင်းရမည့် USDT: **{sellable_usdt:,.2f}** USDT")

        st.divider()
        st.header("Step 2: P2P Sell Results")
        initial_sell_data = pd.DataFrame([{"Seller": "", "USDT Sold": 0.0, "MMK Received": 0}])
        edited_sell_df = st.data_editor(initial_sell_data, num_rows="dynamic", use_container_width=True, key="sell_table")
        
        total_mmk_received = edited_sell_df["MMK Received"].sum()
        total_usdt_check = edited_sell_df["USDT Sold"].sum()
        
        if total_mmk_received > 0:
            # Customer rate based on total MMK received / original USDT
            real_customer_rate = total_mmk_received / total_usdt_in
            
            st.subheader("📋 Final Summary (Sell)")
            sell_summary = f"SUMMARY\n- Total USDT: {total_usdt_in:,.2f}\n- Total MMK to Pay: {total_mmk_received:,.0f}\n- Rate: {real_customer_rate:,.2f}"
            st.code(sell_summary)
            
            st.write(f"🔍 ကျန်ရှိနေသေးသော ရောင်းရန် USDT: **{(sellable_usdt - total_usdt_check):,.2f}** USDT")

# ---------------------------------------------------------
# GOOGLE SHEETS INTEGRATION (Common for both)
# ---------------------------------------------------------
st.divider()
st.header("💾 Save Record")
save_button = st.button("Save to Google Sheets")

if save_button:
    try:
        creds_dict = json.loads(st.secrets["GCP_CREDENTIALS"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open("P2P_History").sheet1
        
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # Determine which tab data to save
        # Note: In a real app, you'd track which tab is active. 
        # Here we save the one that has data.
        if total_mmk > 0:
            row = [now, "BUY", f"{total_mmk:,.0f}", f"{total_usdt_bought:,.2f}", f"{customer_rate:,.2f}", f"{profit_mmk:,.0f}"]
            sheet.append_row(row)
            st.success("✅ Buy Record saved!")
        elif total_usdt_in > 0:
            row = [now, "SELL", f"{total_mmk_received:,.0f}", f"{total_usdt_in:,.2f}", f"{real_customer_rate:,.2f}", "N/A"]
            sheet.append_row(row)
            st.success("✅ Sell Record saved!")
            
    except Exception as e:
        st.error(f"Error: {e}")
