import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import pandas as pd
import plotly.express as px
import numpy as np
from supabase import create_client


url="https://gywtlivqrvxgttetymwh.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd5d3RsaXZxcnZ4Z3R0ZXR5bXdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQzMDQxMTAsImV4cCI6MjA1OTg4MDExMH0.1cL2AKAwyA_exgRE3qGh17KbYXa-gPDl93w-kjvAyAw"
supabase=create_client(url,key)
#https://www.youtube.com/watch?v=dOl51vhOGRc - Authentication
##Username and password
def creds_entered():
     if st.session_state["user"].strip()=="admin@gmail.com" and st.session_state["password"].strip()=="admin123":
        st.session_state["authenticated"] = True     #The session state is saved as authenticated and user does not have to login again
     else:
          st.session_state["authenticated"]=False    #The session state remains unauthenticated and user needs to login to check for fraud
          if not st.session_state["user"]:
              st.warning("Please enter your email.")
          elif not st.session_state["password"]:
              st.warning("Please enter your password.")
          else:
             st.error("Invalid Email/Password. Please signup if you do not have an account") 
             st.link_button("Need help?", "https://fraudguard1.streamlit.app/Contactus")

#https://www.youtube.com/watch?v=dOl51vhOGRc - Authentication
##Login page
def authenticate_user():
    if "authenticated" not in st.session_state:  #If loop runs only if not authenticated
        placeholder=st.empty()
        with placeholder.container():
            st.title ("First, you need to login")
            email=st.text_input("Enter your email: ", value="", max_chars=30, key="user", type="default", help=None, autocomplete=None, on_change=creds_entered, args=None, kwargs=None, placeholder="Type here", disabled=False, label_visibility="visible")
            password=st.text_input("Enter your password: ", value="", max_chars=25, key="password", type="password", help=None, autocomplete=None, on_change=creds_entered, args=None, kwargs=None, placeholder="Type here", disabled=False, label_visibility="visible")
    else:
        if st.session_state["authenticated"]: #If already authenticated, then the loop is broken and the next code is executed
             return True
        else:
            st.title ("First, you need to login")
            email=st.text_input("Enter your email: ", value="", max_chars=30, key="user", type="default", help=None, autocomplete=None, on_change=creds_entered, args=None, kwargs=None, placeholder="Type here", disabled=False, label_visibility="visible")
            password=st.text_input("Enter your password: ", value="", max_chars=25, key="password", type="password", help=None, autocomplete=None, on_change=creds_entered, args=None, kwargs=None, placeholder="Type here", disabled=False, label_visibility="visible")
            return False 

#def loadTransaction():
#    conn = sqlite3.connect('fraud.db')  # New connection
 #   cursor = conn.cursor()  # Create cursor
 #   cursor.execute("SELECT * FROM transaction_z")
 #   results=cursor.fetchall()
 #   columns = [desc[0] for desc in cursor.description]
 #   df_transactions = pd.DataFrame(results, columns=columns)
#    return df_transactions

def loadTransactions():
    try:
        response = (
            supabase.table("Transactions").select("*").execute()    
        )
        results=response.data
        df_transactions=pd.DataFrame(results)
        return df_transactions
    except Exception as e:
        st.error(f"Error loading the transactions: {e}")
        return pd.DataFrame() 

st.markdown('<h1 style="text-align: center;font-size:80px;color:#bad7d9;font-family:Georgia">Dashboard</h1>', unsafe_allow_html=True,)
st.divider()
#https://www.youtube.com/watch?v=Sb0A9i6d320&list=PLHgX2IExbFovFg4DI0_b3EWyIGk-oGRzq
df_transactions=loadTransactions()

total_fraud_transactions=(df_transactions["Fraud_Prediction"]==1).sum()
if total_fraud_transactions>0:
    average_fraud=total_fraud_transactions/df_transactions.shape[0]
else:
    average_fraud=0

col1,col3,col2 = st.columns(3)

with col1:
    st.markdown('<h2 style="text-align: center;font-size:30px;color:#bad7d9;font-family:Georgia">Number of fraud transactions</h2>', unsafe_allow_html=True,)
    st.markdown(f'<h2 style="text-align: center; font-size:30px; color:#bad7d9; font-family:Georgia">{total_fraud_transactions}</h2>', unsafe_allow_html=True)
with col2:
    st.markdown('<h2 style="text-align: center;font-size:30px;color:#bad7d9;font-family:Georgia">Fraud rate</h2>', unsafe_allow_html=True,)
    st.markdown(f'<h2 style="text-align: center; font-size:30px; color:#bad7d9; font-family:Georgia">{average_fraud:.2%}</h2>', unsafe_allow_html=True)
st.markdown("---")
st.link_button("View reports page", "https://fraudguard1.streamlit.app/Reports")
col3,col4=st.columns(2)

#https://www.youtube.com/watch?v=Sb0A9i6d320&list=PLHgX2IExbFovFg4DI0_b3EWyIGk-oGRzq
with col3:
    st.markdown('<h2 style="text-align: center;font-size:30px;color:#bad7d9;font-family:Georgia">Average transaction by fraud</h2>', unsafe_allow_html=True,)

    # Group by 'is_fraud' and calculate the mean transaction amount
    amt_fraud=(
         df_transactions.groupby('Fraud_Prediction')['amount'].mean().reset_index()
)
# Plot the result
    fig_amt_fraud=px.bar(
        amt_fraud,
        x="amount",
        y="Fraud_Prediction",
        orientation="h",
        title="",
        color_discrete_sequence=['blue', 'red'],
        template="plotly"
    )

    st.plotly_chart(fig_amt_fraud)

#https://www.youtube.com/watch?v=Sb0A9i6d320&list=PLHgX2IExbFovFg4DI0_b3EWyIGk-oGRzq
with col4:
    st.markdown('<h2 style="text-align: center;font-size:30px;color:#bad7d9;font-family:Georgia">Distribution of fraud and non-fraud</h2>', unsafe_allow_html=True,)

    fig, ax = plt.subplots(figsize=(6, 4))

    sns.countplot(x='Fraud_Prediction', data=df_transactions)
    ax.set_title('')
    ax.set_xlabel('Is Fraud')
    ax.set_ylabel('Count')
    st.plotly_chart(fig)
