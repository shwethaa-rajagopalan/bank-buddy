import streamlit as st
import hashlib 
from dotenv import load_dotenv
import os
import sqlite3
import pandas as pd

from pages.agent_ui import chat_page
from tools import getCustomerData

load_dotenv()

DB_FILE_NAME = 'customer_data.db'




def hash_password(password):
    """A very basic example of hashing - use a stronger library like bcrypt in production."""
    return hashlib.sha256(password.encode()).hexdigest()

def fetch_password(username):
    conn_read = sqlite3.connect(DB_FILE_NAME)
    query = f"SELECT * FROM USER_LOGIN WHERE USER_ID = {username};"
    result_df = pd.read_sql_query(query, conn_read)
    conn_read.close()
    # print(result_df.iloc[0].to_dict()['password'])
    return result_df.iloc[0].to_dict()['password']

# --- Login Function ---
def login_user(username, password):
    if hash_password(password) == fetch_password(username):
        st.session_state.logged_in = True
        cust_info = getCustomerData(username)
        st.session_state.customer_id = cust_info['customer_id']
        st.session_state.first_name = cust_info['first_name']
        st.session_state.last_name = cust_info['last_name']
        return True
    return False

def initial_flow():
# --- Main Application Logic ---
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "logged_in" in st.session_state and st.session_state.logged_in:
        st.session_state.logged_in = False
        st.experimental_rerun()
    if not st.session_state.logged_in:
        st.title("Login")
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        st.dataframe(pd.read_sql_query("SELECT user_id FROM USER_LOGIN;", sqlite3.connect(DB_FILE_NAME)))
        "hint: password is same as user_id"

        if st.button("Login"):
            if login_user(username_input, password_input):
                st.success("Logged in successfully!")
                st.switch_page("pages/agent_ui.py")

                # chat_page()# Rerun to update content
            else:
                st.error("Invalid username or password.")
    else:
        chat_page()

if __name__ == "__main__":
    st.session_state.logged_in = False
    initial_flow()
    # Force login prompt after page refresh
    