import streamlit as st
import joblib
import pandas as pd
from sklearn.preprocessing import PowerTransformer
from sklearn.preprocessing import LabelEncoder
import datetime
import os
from sklearn.metrics import classification_report
import sqlite3


#https://stackoverflow.com/questions/5137497/find-the-current-directory-and-files-directory
#current_directory = os.path.dirname(os.path.abspath(__file__))  #Obtain absolute path to current working directory

# Construct the full path to xgb_model.pkl, which is in the same directory
#model_path = os.path.join(current_directory, "xgb_model.pkl")

# Load the model from the constructed path
#model = joblib.load(model_path)

#https://www.youtube.com/watch?v=R7aBgKndPxo - Database connection tutorial

model=joblib.load("pages/xgb_model.pk1")
#model2=joblib.load("pages/xgb_model.pk2")
#model3=joblib.load("pages/xgb_model.pk3")
pt = joblib.load("pages/powertransformer.pk1")

label_encoder=joblib.load("pages/label_encoder.pk1")
scaler=joblib.load("pages/scaler.pk1")
#https://www.youtube.com/watch?v=dOl51vhOGRc
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

def dashboard():
# Your df that contains "Time" column


    st.markdown('<h1 style="text-align: center;font-size:80px;color:#bad7d9;font-family:Georgia">Fraud Check</h1>', unsafe_allow_html=True,)
    st.divider()
    col1, col2 = st.columns(2)
    start_time = datetime.datetime(2019, 10, 6, 12, 14, 55)
#https://stackoverflow.com/questions/74949455/combine-date-and-time-inputs-in-streamlit-with-dataframe-time-column
    with col1:
        if st.checkbox("Enter data manually"):
            with st.form("manual_entry"):
                amt = st.number_input("Transaction amount ($)", min_value=0.0, format="%.2f")
                
                trans_date = st.date_input("Enter transaction date", value=datetime.date.today())
                trans_time = st.time_input("Enter transaction time", value=datetime.time(12, 0, 0))
                trans_date_trans_time = datetime.datetime.combine(trans_date, trans_time)
                
                dob = st.date_input("Date of birth")
                merchant = st.selectbox("Enter the merchant", ("fraud_kiplin", "fraud_merchant"))
                category = st.selectbox("Enter the category", ("food","grocery"))
                city = st.text_input("Enter the city")
                data_consent=st.checkbox("I allow Fraud Guard to collect my data for learning purposes")
                submit_button = st.form_submit_button("Submit")
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
                    
                        df_manual["Fraud_Prediction"]=prediction

                        prediction_database=int(prediction[0])
                        addTransaction(amt,trans_date_trans_time,dob,merchant,category,city,prediction_database)


    #                    legitimate_count = df["Fraud_Prediction"].value_counts().get(0, 0)
    #                    st.write(f"Number of Legitimate transactions: {legitimate_count}")
    with col2:        
        if st.checkbox("Upload data"):
            input_data=st.file_uploader("Upload your transaction data") 
    
            if input_data is not None:
                try:
                    df_main = pd.read_csv(input_data)
                    df=df_main.copy()

                    df=df.drop(columns=['Unnamed: 0','first','last','street','lat','long','zip','cc_num','is_fraud'])
                    df=df.drop(columns=['state','merch_lat','merch_long','city_pop','unix_time','gender','job','trans_num']) #Dropcolumns

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
                    if st.checkbox('Show what the dataframe looks like'):
                        st.write(df_new.head(100))
                        st.write('Shape of the dataframe: ',df_new.shape)
                        
    
                    if st.button("Fraud check"):
                        prediction=model.predict(df_new)
                        df_new["fraud_prediction"]=prediction
                        fraud_count =(prediction==1).sum()                   
                        if (fraud_count> 0):
                            st.error(f"⚠️ {fraud_count}Fraudulent Transactions Detected! ")
                        else:
                            st.success("✅ No fraudulent transactions")
                    
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
                            addTransaction(amt,trans_date_trans_time,dob,merchant,category,city,prediction)

    #                    st.write(f"Number of fraudulent transactions: {fraud_count}")

    #                   fraud_count = df_new["Fraud_Prediction"].value_counts().get(1, 0)
    #                    st.error(f"⚠️ Fraudulent Transaction Detected! {fraud_count}")

    #                    legitimate_count = df_new["Fraud_Prediction"].value_counts().get(0, 0)
    #                    st.write(f"Number of Legitimate transactions: {legitimate_count}")

    #                    class_report = classification_report(y, prediction)
    #                   st.text(class_report)
                except Exception as e:
                    st.error(f"Error processing file: {e}")  # Show error if reading fails


    if st.button("Logout"):
       st.success("Logout successful!")
       st.session_state.authenticated=False
       st.session_state.page = "Home",

def addTransaction(a,b,c,d,x,y,z):
    conn = sqlite3.connect('fraud.db')  # New connection
    cursor = conn.cursor()  # Create cursor
    cursor.execute(
        """
CREATE TABLE IF NOT EXISTS transaction_z (AMOUNT REAL,TRANSACTION_PERIOD TEXT(50),DOB TEXT(50),MERCHANT TEXT(50),CATEGORY TEXT(50),CITY TEXT(50),FRAUD_PREDICTION INTEGER)
"""
    )
    cursor.execute("INSERT INTO transaction_z VALUES (?,?,?,?,?,?,?)", (a,b,c,d,x,y,z))
    conn.commit()

if authenticate_user():
    dashboard() 