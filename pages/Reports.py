import streamlit as st
import sqlite3
import pandas as pd

def creds_entered():
     if st.session_state["user"].strip()=="admin" and st.session_state["password"].strip()=="admin123":
        st.session_state["authenticated"] = True
     else:
          st.session_state["authenticated"]=False
          if not st.session_state["user"]:
              st.warning("Please enter your username.")
          elif not st.session_state["password"]:
              st.warning("Please enter your password.")
          else:
             st.error("Invalid Username/Password") 

#https://www.youtube.com/watch?v=dOl51vhOGRc
def authenticate_user():
    if "authenticated" not in st.session_state:
        placeholder=st.empty()
        with placeholder.container():
            st.title ("First, you need to login")
            username=st.text_input("Enter your username: ", value="", max_chars=None, key="user", type="default", help=None, autocomplete=None, on_change=creds_entered, args=None, kwargs=None, placeholder="Type here", disabled=False, label_visibility="visible")
            password=st.text_input("Enter your password: ", value="", max_chars=None, key="password", type="password", help=None, autocomplete=None, on_change=creds_entered, args=None, kwargs=None, placeholder="Type here", disabled=False, label_visibility="visible")
    else:
        if st.session_state["authenticated"]:
             return True
        else:
            st.title ("First, you need to login")
            username=st.text_input("Enter your username: ", value="", max_chars=None, key="user", type="default", help=None, autocomplete=None, on_change=creds_entered, args=None, kwargs=None, placeholder="Type here", disabled=False, label_visibility="visible")
            password=st.text_input("Enter your password: ", value="", max_chars=None, key="password", type="password", help=None, autocomplete=None, on_change=creds_entered, args=None, kwargs=None, placeholder="Type here", disabled=False, label_visibility="visible")
            return False 


def reports():
    st.markdown('<h1 style="text-align: center;font-size:80px;color:#bad7d9;font-family:Georgia">Reports</h1>', unsafe_allow_html=True,)
    st.markdown("Welcome to your reports page!")
    col2, col3 = st.columns(2)
    

    with col2:
        st.header("Model performance")
        st.image("pages/xgboost_confusion_matrix.png")


    with col3:
        st.subheader("Model performance")
        conn = sqlite3.connect('fraud.db')  # New connection
        cursor = conn.cursor()  # Create cursor
        cursor.execute("SELECT * FROM xgb_classification_report")
        results=cursor.fetchall()
        xgb_report = pd.DataFrame(results)
        st.dataframe(xgb_report)

    st.header("Transactions") 
    displayTransaction()


def displayTransaction():
    conn = sqlite3.connect('fraud.db')  # New connection
    cursor = conn.cursor()  # Create cursor
    cursor.execute("SELECT * FROM transaction_z")
    results=cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df_transactions = pd.DataFrame(results, columns=columns)
    st.write("Click on the columns to sort them!")
    st.dataframe(df_transactions.head(10000))
    st.success("Transactions have been displayed on table")

if authenticate_user():
    reports() 
      
