import streamlit as st
import joblib
import pandas as pd
from sklearn.preprocessing import PowerTransformer
from sklearn.preprocessing import LabelEncoder
import os
from sklearn.metrics import classification_report
import sqlite3
from datetime import datetime,date,time 
from supabase import create_client


#https://www.youtube.com/watch?v=R7aBgKndPxo - Database connection tutorial

##Load trained xgb model
model=joblib.load("pages/xgb_model.pk1")
##Load power transformer used in backend
pt = joblib.load("pages/powertransformer.pk1")
##Load encoder used in back end
label_encoder=joblib.load("pages/label_encoder.pk1")
##Load scaler used in back end
scaler=joblib.load("pages/scaler.pk1")

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
##Fraud check
def fraudcheck():

    st.markdown('<h1 style="text-align: center;font-size:80px;color:#bad7d9;font-family:Georgia">Fraud Check</h1>', unsafe_allow_html=True,)
    st.divider()
    col1, col2 = st.columns(2)
    start_time = datetime(1950, 10, 6, 12, 14, 55)
#https://stackoverflow.com/questions/74949455/combine-date-and-time-inputs-in-streamlit-with-dataframe-time-column
    with col1:
        if st.checkbox("Enter data manually"):
            with st.form("manual_entry"):
                amt = st.number_input("Transaction amount ($)", min_value=0.0, format="%.2f")
                
                trans_date = st.date_input("Enter transaction date", value=date.today())
                trans_time = st.time_input("Enter transaction time", value=time(12, 0, 0))
                trans_date_trans_time = datetime.combine(trans_date, trans_time)
                
                dob = st.date_input("Date of birth")
                merchant = st.selectbox("Enter the merchant", ("fraud_kiplin", "fraud_merchant"))
                category = st.selectbox("Enter the category", ("food","grocery"))
                city = st.text_input("Enter the city")
                data_consent=st.checkbox("I allow Fraud Guard to collect my data for learning purposes")
                
                submit_button = st.form_submit_button("Submit data")
                
                if submit_button:
                    if not data_consent:
                        st.error("You must allow Fraud Guard to store data to check for fraud")
                    else:
                        df=pd.DataFrame([[amt, trans_date_trans_time, dob, merchant,category, city]],
                                        columns=["amt", "trans_date_trans_time", "dob", "merchant","category", "city"])
                        
                        df_manual=df.copy()
                        df['amt'] = pt.transform(df[['amt']])


                        df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'])
                        df['transaction_period'] = df['trans_date_trans_time'].view('int64') // 10**9  # Convert to seconds
                        df.drop(columns=['trans_date_trans_time'], inplace=True)  # Drop original column

                        df['dob'] = pd.to_datetime(df['dob'])
                        df['new_dob'] = df['dob'].view('int64') // 10**9  # Convert to seconds
                        df.drop(columns=['dob'], inplace=True)  # Drop original column

                        df['merchant_encoded'] = label_encoder.fit_transform(df['merchant'].fillna('Unknown'))   #Encode merchant
                        df.drop(columns=['merchant'], inplace=True)   #Drop old merchant column

                        df['category_encoded'] = label_encoder.fit_transform(df['category'].fillna('Unknown'))
                        df.drop(columns=['category'], inplace=True)

                        df['city_encoded'] = label_encoder.fit_transform(df['city'].fillna('Unknown'))
                        df.drop(columns=['city'], inplace=True)      

    # Scale the features
                        X_scaled = scaler.transform(df)

    # Convert X_scaled (NumPy array) back to a DataFrame with the original columns
                        X_scaled_df = pd.DataFrame(X_scaled, columns=df.columns)

    # Now you can use .iloc[] on the DataFrame
                        df_new = X_scaled_df.iloc[:, [0, 3, 4, 5, 1, 2]]  
                    
                        prediction=model.predict(df)
                        df["Fraud_Prediction"] = prediction   #Add prediction
                        fraud_count = df["Fraud_Prediction"].value_counts().get(1, 0)
                        if prediction[0] == 1:
                                st.error(f"⚠️ {fraud_count}Fraudulent Transactions Detected! ")
                        else:
                                st.success("✅ No fraudulent transactions")
                                st.success("You can now enter new data to be checked")
                    
                        df_manual["Fraud_Prediction"]=prediction

                        prediction_database=int(prediction[0])
                        addTransaction(amt,trans_date_trans_time,dob,merchant,category,city,prediction_database)

    with col2:        
        if st.checkbox("Upload data"):
            input_data=st.file_uploader("Upload your transaction data") 
#https://discuss.streamlit.io/t/catching-the-error-message-in-file-upload/41322/2 - File exception errors
            if input_data is not None:
                try:
                    filename, file_extension = os.path.splitext(input_data.name)

                    if (file_extension == ".csv") is True:
    
                        df_main = pd.read_csv(input_data)
                        df=df_main.copy() #Dropcolumns

                        df['amt'] = pt.transform(df[['amt']])


                        df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'])
                        df['transaction_period'] = df['trans_date_trans_time'].view('int64') // 10**9  # Convert to seconds
                        df.drop(columns=['trans_date_trans_time'], inplace=True)  # Drop original column

                        df['dob'] = pd.to_datetime(df['dob'])
                        df['new_dob'] = df['dob'].view('int64') // 10**9  # Convert to seconds
                        df.drop(columns=['dob'], inplace=True)  # Drop original column

                        df['merchant_encoded'] = label_encoder.fit_transform(df['merchant'].fillna('Unknown'))   #Encode merchant
                        df.drop(columns=['merchant'], inplace=True)   #Drop old merchant column

                        df['category_encoded'] = label_encoder.fit_transform(df['category'].fillna('Unknown'))
                        df.drop(columns=['category'], inplace=True)

                        df['city_encoded'] = label_encoder.fit_transform(df['city'].fillna('Unknown'))
                        df.drop(columns=['city'], inplace=True)        

        # Scale the features
                        X_scaled = scaler.transform(df)

        # Convert X_scaled (NumPy array) back to a DataFrame with the original columns
                        X_scaled_df = pd.DataFrame(X_scaled, columns=df.columns)

                        df_new = X_scaled_df.iloc[:, [0, 3, 4, 5, 1, 2]]              
        
                        if st.button("Fraud check"):
                            prediction=model.predict(df)
                            df["Fraud_Prediction"] = prediction   #Add prediction
                            fraud_count = df["Fraud_Prediction"].value_counts().get(1, 0)
                            if prediction[0] == 1:
                                    st.error(f"⚠️ {fraud_count}Fraudulent Transactions Detected! ")
                            else:
                                    st.success("✅ No fraudulent transactions")
                                    st.success("You can now upload new data to be checked")

                            df_main["Fraud_Prediction"] = prediction  # Add predictions
        #https://stackoverflow.com/questions/43221208/iterate-over-pandas-dataframe-using-itertuples                                                 
                        
                            for row in df_main.itertuples(index=False):
                                amt=row.amt
                                trans_date_trans_time=row.trans_date_trans_time
                                dob=row.dob
                                merchant=row.merchant
                                category=row.category
                                city=row.city
                                prediction=row.Fraud_Prediction
                                addTransactions(amt,trans_date_trans_time,dob,merchant,category,city,prediction)
                    else:
                        st.error('File type is not csv')
                except Exception as e:
                    st.error(f"Error processing file: {e}")  # Show error if reading fails

    if st.button("Logout"):
       st.success("Logout successful!")
       st.session_state.authenticated=False
       st.session_state.page = "Home",

# https://www.tutorialspoint.com/How-to-convert-Python-date-in-JSON-format - How to convert datetime in json format
#https://www.geeksforgeeks.org/how-to-fix-datetime-datetime-not-json-serializable-in-python/ - Serializing datetime
 
def addTransactions(a,b,c,d,x,y,z):
    conn = sqlite3.connect('fraud.db')  # New connection
    cursor = conn.cursor()  # Create cursor
    cursor.execute(
        """
CREATE TABLE IF NOT EXISTS transaction_z (AMOUNT REAL,TRANSACTION_PERIOD TEXT(50),DOB TEXT(50),MERCHANT TEXT(50),CATEGORY TEXT(50),CITY TEXT(50),FRAUD_PREDICTION INTEGER)
"""
    )
    cursor.execute("INSERT INTO transaction_z VALUES (?,?,?,?,?,?,?)", (a,b,c,d,x,y,z))
    conn.commit()

def addTransaction(amt,trans_date_trans_time,dob,merchant,category,city,prediction):
    data = {
        "amount": amt,
        "Transaction_time":  trans_date_trans_time.isoformat() if isinstance(trans_date_trans_time, (datetime, date)) else trans_date_trans_time,
        "Dob":  dob.isoformat() if isinstance(dob, (datetime,date)) else dob,
        "Merchant": merchant,
        "Category": category,
        "City": city,
        "Fraud_Prediction":prediction
      
    }
    response = supabase.table("Transactions").insert(data).execute()
   
if authenticate_user():
    fraudcheck() 
