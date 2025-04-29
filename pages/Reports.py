import streamlit as st
import sqlite3
import pandas as pd
from supabase import create_client

#https://www.youtube.com/watch?v=dU7GwCOgvNY - How to use supabase database
#Url and key for supabase database connection
url="https://gywtlivqrvxgttetymwh.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd5d3RsaXZxcnZ4Z3R0ZXR5bXdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQzMDQxMTAsImV4cCI6MjA1OTg4MDExMH0.1cL2AKAwyA_exgRE3qGh17KbYXa-gPDl93w-kjvAyAw"
#Create client function to create a connection
supabase=create_client(url,key)

#https://www.youtube.com/watch?v=dOl51vhOGRc - How to create authentication
##Authentication
def creds_entered():
     if st.session_state["user"].strip()=="admin@gmail.com" and st.session_state["password"].strip()=="admin123":
        st.session_state["authenticated"] = True     #The session state is saved as authenticated if the credentials are correct
     else:
          st.session_state["authenticated"]=False   #The session is unauthenticated as the credentials are incorrect
          if not st.session_state["user"]:
              #Login to get authenticated
              st.warning("Please enter your email.")
          elif not st.session_state["password"]:
              st.warning("Please enter your password.")
        #Error message if credentials incorrect
          else:
             st.error("Invalid Email/Password. Please signup if you do not have an account") 
             st.link_button("Need help?", "https://fraudguard1.streamlit.app/Contactus")

#https://www.youtube.com/watch?v=dOl51vhOGRc - Authentication
def authenticate_user():
    if "authenticated" not in st.session_state:
        placeholder=st.empty()
        with placeholder.container():
            st.title ("First, you need to login")
            #login to obtain authenticated session state
            email=st.text_input("Enter your email: ", value="", max_chars=30, key="user", type="default", help=None, autocomplete=None, on_change=creds_entered, args=None, kwargs=None, placeholder="Type here", disabled=False, label_visibility="visible")
            password=st.text_input("Enter your password: ", value="", max_chars=25, key="password", type="password", help=None, autocomplete=None, on_change=creds_entered, args=None, kwargs=None, placeholder="Type here", disabled=False, label_visibility="visible")
    else:
        if st.session_state["authenticated"]:
             return True    #Session state is authenticated
        else:
            st.title ("First, you need to login")
            email=st.text_input("Enter your email: ", value="", max_chars=30, key="user", type="default", help=None, autocomplete=None, on_change=creds_entered, args=None, kwargs=None, placeholder="Type here", disabled=False, label_visibility="visible")
            password=st.text_input("Enter your password: ", value="", max_chars=25, key="password", type="password", help=None, autocomplete=None, on_change=creds_entered, args=None, kwargs=None, placeholder="Type here", disabled=False, label_visibility="visible")
            return False 

##Reports page
def reports():
    st.markdown('<h1 style="text-align: center;font-size:80px;color:#bad7d9;font-family:Georgia">Reports</h1>', unsafe_allow_html=True,)
    st.markdown('<div style="color:#bad7d9;font-size:25px;font-family:roboto">Welcome to the reports page</div>',unsafe_allow_html=True)
    col2, col3 = st.columns(2)
    
    #Display model confusion matrix
    with col2:
        st.header("Model performance")
        st.image("pages/xgboost_confusion_matrix.png")

    #Display model performance
    with col3:
        conn = sqlite3.connect('fraud.db')  # New connection
        cursor = conn.cursor()  # Create cursor
        #Model performance data stored in sqlite database
        cursor.execute("SELECT * FROM xgb_classification_report")
        results=cursor.fetchall()
        xgb_report = pd.DataFrame(results)
        st.dataframe(xgb_report)

    st.header("Transactions") 
    displayTransaction()

        ##Logout button

       
#Display transactions stored in supabase database
def displayTransaction():
    #Select all data stored in "Transactions" column
    response = (
        supabase.table("Transactions").select("*").execute()    
    )
    results=response.data
    #All data fetched is stored in a dataframe
    df_transactions=pd.DataFrame(results)
    st.write("Click on the columns to sort them!")
    st.link_button("View fraud analyses in dashboard", "https://fraudguard1.streamlit.app/Dashboard")
    st.dataframe(df_transactions.head(10000))
    st.success("Transactions have been displayed on table")
    if st.button("Logout"):
       st.success("Logout successful!")
       st.session_state.authenticated=False   #Session is broken and needs to be reauthenticated

if authenticate_user():
    reports() 
      
