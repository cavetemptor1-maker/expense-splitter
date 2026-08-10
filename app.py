import time
import requests
import streamlit as st
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Smart Monthly Expense Splitter", page_icon="💖", layout="wide")

# --- Custom CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%); color: #333; }
    h1 { color: #d81b60; text-align: center; text-transform: uppercase; letter-spacing: 2px; }
    .total-box { background: #fff0f3; padding: 15px; border-radius: 10px; border: 1px solid #ffb6c1; margin-bottom: 10px; }
    .settlement-box { background: linear-gradient(135deg, #fff0f3 0%, #ffe4e8 100%); border: 2px solid #ff758c; padding: 15px; border-radius: 10px; text-align: center; color: #d81b60; font-weight: bold; font-size: 1.2em; }
    .item-card { background: white; padding: 10px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #ffb6c1; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# --- JSONBin Setup ---
try:
    API_KEY = st.secrets["JSONBIN_KEY"]
    BIN_ID = st.secrets["JSONBIN_BIN_ID"]
    BASE_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
    HEADERS = {
        "Content-Type": "application/json",
        "X-Master-Key": API_KEY
    }
except Exception as e:
    st.error("⚠️ Streamlit Secrets में JSONBin की ID या Key नहीं मिली है!")
    st.stop()

def load_expenses():
    try:
        req = requests.get(f"{BASE_URL}/latest", headers=HEADERS)
        if req.status_code == 200:
            data = req.json()
            return data.get("record", [])
        return []
    except:
        return []

def save_expenses(expenses):
    try:
        requests.put(BASE_URL, json=expenses, headers=HEADERS)
    except Exception as e:
        st.error(f"Error saving to JSONBin: {e}")

# --- Session State Init ---
if "expenses" not in st.session_state:
    st.session_state.expenses = load_expenses()
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

st.markdown("<h1>✨ Monthly Expense Splitter ✨</h1>", unsafe_allow_html=True)

# --- Clear All Section ---
col_head1, col_head2 = st.columns([4, 2])
with col_head2:
    st.markdown("#### 🗑️ Clear All Data")
    clear_pwd = st.text_input("Enter Password (1307):", type="password", key="clear_pwd")
    if st.button("Confirm Clear All"):
        if clear_pwd == "1307":
            st.session_state.expenses = []
            save_expenses(st.session_state.expenses)
            st.success("All data cleared successfully!")
            st.rerun()
        elif clear_pwd:
            st.error("Incorrect Password!")

st.markdown("---")

# --- Add/Edit Form Section ---
edit_item = None
if st.session_state.edit_id:
    edit_item = next((e for e in st.session_state.expenses if e["id"] == st.session_state.edit_id), None)
    col_t1, col_t2 = st.columns([4, 1])
    with col_t1:
        st.markdown(f"### ✏️ Update Expense: {edit_item['name'] if edit_item else ''}")
    with col_t2:
        if st.button("❌ Cancel Edit"):
            st.session_state.edit_id = None
            st.rerun()
else:
    st.markdown("### ➕ Add New Expense")

def_name = edit_item["name"] if edit_item else ""
def_amount = float(edit_item["amount"]) if edit_item else 0.0

def_date = datetime.today().date()
if edit_item:
    try:
        def_date = datetime.strptime(edit_item["date"], "%Y-%m-%d").date()
    except:
        pass

cat_options = ["grocery", "personalS", "personalA"]
def_cat_idx = cat_options.index(edit_item["category"]) if edit_item and edit_item["category"] in cat_options else Hello! I'm here and ready to assist. 

What would you like to focus on today?