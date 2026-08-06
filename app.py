import json
import os
import time
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

DATA_FILE = "expenses.json"

# --- Functions ---
def load_expenses():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_expenses(expenses):
    with open(DATA_FILE, "w") as f:
        json.dump(expenses, f, indent=4)

# --- Session State Init ---
if "expenses" not in st.session_state:
    st.session_state.expenses = load_expenses()
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

st.markdown("<h1>✨ Monthly Expense Splitter ✨</h1>", unsafe_allow_html=True)

# --- Clear All Section (Fixed) ---
col_head1, col_head2 = st.columns([4, 2])
with col_head2:
    st.markdown("#### 🗑️ Clear All Data")
    clear_pwd = st.text_input("Enter Password (1307):", type="password", key="clear_pwd")
    if st.button("Confirm Clear All"):
        if clear_pwd == "1307":
            st.session_state.expenses = []
            save_expenses(st.session_state.expenses)
            st.success("All data cleared!")
            st.rerun()
        elif clear_pwd:
            st.error("Incorrect Password!")

st.markdown("---")

# --- Add/Edit Form Section (Fixed) ---
edit_item = None
if st.session_state.edit_id:
    # Find the item being edited
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

# Determine Default Values for Form
def_name = edit_item["name"] if edit_item else ""
def_amount = float(edit_item["amount"]) if edit_item else 0.0

def_date = datetime.today().date()
if edit_item:
    try:
        def_date = datetime.strptime(edit_item["date"], "%Y-%m-%d").date()
    except:
        pass

cat_options = ["grocery", "personalS", "personalA"]
def_cat_idx = cat_options.index(edit_item["category"]) if edit_item and edit_item["category"] in cat_options else 0

paid_options = ["S", "A"]
def_paid_idx = paid_options.index(edit_item["paidBy"]) if edit_item and edit_item["paidBy"] in paid_options else 0

# The Form
with st.form("expense_form", clear_submit=True):
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        name = st.text_input("Item Name", value=def_name, placeholder="e.g. Milk")
    with c2:
        amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f", value=def_amount)
    with c3:
        date = st.date_input("Date", value=def_date)
    with c4:
        category = st.selectbox("Category", options=cat_options, index=def_cat_idx, 
                                format_func=lambda x: {"grocery":"Core Grocery", "personalS":"Personal S", "personalA":"Personal A"}[x])
    with c5:
        paid_by = st.selectbox("Paid By", options=paid_options, index=def_paid_idx, format_func=lambda x: f"Paid by: {x}")

    submit_label = "💾 Save Updates" if edit_item else "➕ Add Expense"
    submitted = st.form_submit_button(submit_label)

    if submitted:
        if not name.strip() or amount <= 0:
            st.warning("Please enter a valid item name and amount.")
        else:
            if edit_item:
                # Update existing item
                for exp in st.session_state.expenses:
                    if exp["id"] == st.session_state.edit_id:
                        exp["name"] = name
                        exp["amount"] = float(amount)
                        exp["date"] = str(date)
                        exp["category"] = category
                        exp["paidBy"] = paid_by
                st.session_state.edit_id = None
                st.success("Expense updated!")
            else:
                # Add new item (No password required here)
                new_expense = {
                    "id": str(time.time()),
                    "name": name,
                    "amount": float(amount),
                    "date": str(date),
                    "category": category,
                    "paidBy": paid_by
                }
                st.session_state.expenses.append(new_expense)
                st.success("Expense added successfully!")
            
            save_expenses(st.session_state.expenses)
            st.rerun()

st.markdown("---")

# --- Display Columns ---
col_groc, col_pers, col_settle = st.columns(3)

# Calculate Totals
groc_sum, pers_s_sum, pers_a_sum = 0.0, 0.0, 0.0
total_paid_s, total_paid_a = 0.0, 0.0

for exp in st.session_state.expenses:
    if exp["paidBy"] == "S": total_paid_s += exp["amount"]
    if exp["paidBy"] == "A": total_paid_a += exp["amount"]
    
    if exp["category"] == "grocery": groc_sum += exp["amount"]
    elif exp["category"] == "personalS": pers_s_sum += exp["amount"]
    elif exp["category"] == "personalA": pers_a_sum += exp["amount"]

def render_expense_item(exp):
    """Helper function to show card and Edit/Delete controls"""
    st.markdown(f"""
        <div class="item-card">
            <b>{exp['name']}</b> - ₹{exp['amount']:.2f}<br>
            <small>Paid by {exp['paidBy']} | 📅 {exp['date']}</small>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander(f"⚙️ Manage '{exp['name']}'"):
        pwd = st.text_input("Password (1307):", type="password", key=f"pwd_{exp['id']}")
        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("✏️ Edit", key=f"edit_{exp['id']}"):
                if pwd == "1307":
                    st.session_state.edit_id = exp['id']
                    st.rerun()
                else:
                    st.error("Wrong Password!")
        with bc2:
            if st.button("🗑️ Delete", key=f"del_{exp['id']}"):
                if pwd == "1307":
                    st.session_state.expenses = [e for e in st.session_state.expenses if e["id"] != exp["id"]]
                    save_expenses(st.session_state.expenses)
                    st.rerun()
                else:
                    st.error("Wrong Password!")

# Column 1: Grocery
with col_groc:
    st.markdown("### 🛒 Grocery Items")
    for exp in [e for e in st.session_state.expenses if e["category"] == "grocery"]:
        render_expense_item(exp)
    
    st.markdown(f"""
        <div class="total-box">
            <b>Total Grocery:</b> ₹{groc_sum:.2f}<br>
            <hr style="margin:5px 0;">
            <b>S's Share (50%):</b> ₹{groc_sum/2:.2f}<br>
            <b>A's Share (50%):</b> ₹{groc_sum/2:.2f}
        </div>
    """, unsafe_allow_html=True)

# Column 2: Personal Expenses
with col_pers:
    st.markdown("### 💼 Personal Expenses")
    st.markdown("<b>👤 Personal of S</b>", unsafe_allow_html=True)
    for exp in [e for e in st.session_state.expenses if e["category"] == "personalS"]:
        render_expense_item(exp)

    st.markdown("<br><b>👤 Personal of A</b>", unsafe_allow_html=True)
    for exp in [e for e in st.session_state.expenses if e["category"] == "personalA"]:
        render_expense_item(exp)

    st.markdown(f"""
        <div class="total-box">
            <b>Total Personal S:</b> ₹{pers_s_sum:.2f}<br>
            <b>Total Personal A:</b> ₹{pers_a_sum:.2f}
        </div>
    """, unsafe_allow_html=True)

# Column 3: Settlement
with col_settle:
    st.markdown("### 💳 Who Paid What")
    st.markdown(f"""
        <div class="total-box">
            <b>S Actually Paid:</b> ₹{total_paid_s:.2f}<br>
            <b>A Actually Paid:</b> ₹{total_paid_a:.2f}
        </div>
    """, unsafe_allow_html=True)

    s_should_pay = (groc_sum / 2) + pers_s_sum
    a_should_pay = (groc_sum / 2) + pers_a_sum
    
    s_balance = total_paid_s - s_should_pay
    a_balance = total_paid_a - a_should_pay

    settlement_msg = "All settled up! 🎉"
    if s_balance > 0.01:
        settlement_msg = f"A owes S: ₹{abs(s_balance):.2f}"
    elif a_balance > 0.01:
        settlement_msg = f"S owes A: ₹{abs(a_balance):.2f}"

    st.markdown(f"""
        <div class="settlement-box">
            {settlement_msg}
        </div>
    """, unsafe_allow_html=True)