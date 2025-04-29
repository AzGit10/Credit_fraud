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


#https://www.youtube.com/watch?v=R7aBgKndPxo - Database connection tutorial - SQlite

##Load trained xgb model
model=joblib.load("pages/xgb_model.pk1")
##Load power transformer used in backend
pt = joblib.load("pages/powertransformer.pk1")
##Load encoder used in back end
label_encoder=joblib.load("pages/label_encoder.pk1")
##Load scaler used in back end
scaler=joblib.load("pages/scaler.pk1")

#https://www.youtube.com/watch?v=dU7GwCOgvNY - How to use supabase database
#Url and key for supabase database connection
url="https://gywtlivqrvxgttetymwh.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd5d3RsaXZxcnZ4Z3R0ZXR5bXdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQzMDQxMTAsImV4cCI6MjA1OTg4MDExMH0.1cL2AKAwyA_exgRE3qGh17KbYXa-gPDl93w-kjvAyAw"
#Create client function to create a connection
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
            #Email and password to authenticate
            email=st.text_input("Enter your email: ", value="", max_chars=30, key="user", type="default", help=None, autocomplete=None, on_change=creds_entered, args=None, kwargs=None, placeholder="Type here", disabled=False, label_visibility="visible")
            password=st.text_input("Enter your password: ", value="", max_chars=25, key="password", type="password", help=None, autocomplete=None, on_change=creds_entered, args=None, kwargs=None, placeholder="Type here", disabled=False, label_visibility="visible")
    else:
        if st.session_state["authenticated"]: #If already authenticated, then the loop is broken and the next code is executed (FraudCheck page opened)
             return True    #No need to authenticate
        else: #If not authenticated then you need to login again with your email and password
            st.title ("First, you need to login")
            email=st.text_input("Enter your email: ", value="", max_chars=30, key="user", type="default", help=None, autocomplete=None, on_change=creds_entered, args=None, kwargs=None, placeholder="Type here", disabled=False, label_visibility="visible")
            password=st.text_input("Enter your password: ", value="", max_chars=25, key="password", type="password", help=None, autocomplete=None, on_change=creds_entered, args=None, kwargs=None, placeholder="Type here", disabled=False, label_visibility="visible")
            return False 
##Fraud check
def fraudcheck():

    st.markdown('<h1 style="text-align: center;font-size:80px;color:#bad7d9;font-family:Georgia">Fraud Check</h1>', unsafe_allow_html=True,)
    st.divider()
    
    st.markdown('<div style="color:#bad7d9;font-size:23px;font-family:roboto">How to use FraudGuard?</div>',unsafe_allow_html=True)
    st.markdown('<div style="color:#bad7d9;font-size:20px;font-family:roboto">1) Select if you want to enter data manually or by uploading transaction .csv file</div>',unsafe_allow_html=True)
    st.markdown('<div style="color:#bad7d9;font-size:20px;font-family:roboto">2) Enter the data manually or upload a file. Then click on the "Check for fraud" button </div>',unsafe_allow_html=True)
    st.markdown('<div style="color:#bad7d9;font-size:20px;font-family:roboto">3) The results of the check will be displayed in a couple of seconds</div>',unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    start_time = datetime(1950, 10, 6, 12, 14, 55)

#https://stackoverflow.com/questions/74949455/combine-date-and-time-inputs-in-streamlit-with-dataframe-time-column - Combining transaction date and time
    ##Manual data entry fraud check
    with col1:
        if st.checkbox("Enter data manually"):
            with st.form("manual_entry"):
                amt = st.number_input("Transaction amount ($)", min_value=0.0,max_value=1000000.0, format="%.2f")  #Amount
                
                #Transaction date and time - Two fields combined to make this
                trans_date = st.date_input("Enter transaction date", value=date.today())
                trans_time = st.time_input("Enter transaction time", value=time(12, 0, 0))
                trans_date_trans_time = datetime.combine(trans_date, trans_time)
                
                #Date of birth 
                dob = st.date_input("Date of birth")

                #Pick merchant the transaction was made through
                merchant = st.selectbox("Enter the merchant", ("fraud_Rippin,Kub and Mann", "fraud_Heller, Gutmann and Zieme","fraud_Lind-Buckridge","fraud_Kutch","fraud_Keeling","fraud_kirlin and Sons","fraud_sporer-keebler","fraud_Haley Group","fraud_Johnston-Casper","fraud_Daugherty LLC","fraud_Romaguera Ltd","fraud_Reichel LLC","fraud_Goyette,Howell and Collier","fraud_kilback Group","fraud_Feil, Hilpert and Koss"))
                
                #Pick the reason the transaction was made
                category = st.selectbox("Enter the category", ("gas_transport","grocery_pos","personal_care","health_fitness","misc_pos","travel","kids_pets","home","food_dining","entertainment"))

                #Pick the city at which the transaction took place
                city = st.text_input("Enter the city", max_chars=30)

                #Consent for data to be used
                data_consent=st.checkbox("I allow Fraud Guard to collect my data for learning purposes")
                
                #Submit button to submit the data
                submit_button = st.form_submit_button("Submit data")
                
                ##Submit button checks
                if submit_button:
                    #If consent box not ticked - error message displayed
                    if not data_consent:
                        st.error("You must allow Fraud Guard to store data to check for fraud")
                    #Condition for amount field - Amount cannot be 0
                    elif amt==0.0:
                        st.error("Please enter a valid amount")  
                    #Condition for city field - Characters need to be more than 1
                    elif len(city)<=1:
                        st.error("Please enter a valid city")      
                    else:  #If consent button ticked - all the data entered is stored in a dataframe
                        df=pd.DataFrame([[amt, trans_date_trans_time, dob, merchant,category, city]],
                                        columns=["amt", "trans_date_trans_time", "dob", "merchant","category", "city"])
                        
                        df_manual=df.copy()
                    ##Data preprocessing
                        #Normalising amount using power transformer
                        df['amt'] = pt.transform(df[['amt']])

                        #Convert to datetime object
                        df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'])
                        df['transaction_period'] = df['trans_date_trans_time'].view('int64') // 10**9  # Convert to seconds
                        df.drop(columns=['trans_date_trans_time'], inplace=True)  # Drop original column

                        #Convert to datetime object
                        df['dob'] = pd.to_datetime(df['dob'])
                        df['new_dob'] = df['dob'].view('int64') // 10**9  # Convert to seconds
                        df.drop(columns=['dob'], inplace=True)  # Drop original column

                        ##Encode categorical variables
                        #Encode merchant
                        df['merchant_encoded'] = label_encoder.fit_transform(df['merchant'].fillna('Unknown'))   #Encode merchant
                        df.drop(columns=['merchant'], inplace=True)   #Drop old merchant column

                        #Encode category
                        df['category_encoded'] = label_encoder.fit_transform(df['category'].fillna('Unknown'))
                        df.drop(columns=['category'], inplace=True)

                        #Encode city
                        df['city_encoded'] = label_encoder.fit_transform(df['city'].fillna('Unknown'))
                        df.drop(columns=['city'], inplace=True)      

             # Scale the features
                        X_scaled = scaler.transform(df)

             # Convert X_scaled (NumPy array) back to a DataFrame with the original columns
                        X_scaled_df = pd.DataFrame(X_scaled, columns=df.columns)

             # Using .iloc[] on the DataFrame to position columns correctly
                        df_new = X_scaled_df.iloc[:, [0, 3, 4, 5, 1, 2]]  
                    
                    ##Model prediction
                        #Store models predictions for data in prediction variable
                        prediction=model.predict(df)
                        #Add prediction column to the dataset
                        df["Fraud_Prediction"] = prediction  
                        #Obtain the number of fraud
                        #https://www.geeksforgeeks.org/how-to-extract-the-value-names-and-counts-from-value_counts-in-pandas/
                        fraud_count = df["Fraud_Prediction"].value_counts().get(1, 0)
                        #If number of frauds more than 0 then display error message
                        if fraud_count>0:
                                st.error(f"⚠️ {fraud_count}Fraudulent Transactions Detected! ")
                        #If there are no frauds then a success message displayed
                        else:
                                st.success("✅ No fraudulent transactions")
                                st.success("You can now enter new data to be checked")
                                return True
                    
                        df_manual["Fraud_Prediction"]=prediction

                        #Store the first value since the prediction is stored as an array
                        prediction_database=int(prediction[0])
                        #Add the transaction to the database
                        addTransaction(amt,trans_date_trans_time,dob,merchant,category,city,prediction_database)
    ##Upload file for fraud checkk
    with col2:    
        #Upload file    
        if st.checkbox("Upload data"):
            input_data=st.file_uploader("Upload your transaction data") 
#https://discuss.streamlit.io/t/catching-the-error-message-in-file-upload/41322/2 - File exception errors
            #If the file is not e
            if input_data is not None:
               
                try:
                    #Obtain the file extension
                    filename, file_extension = os.path.splitext(input_data.name)
                    #If the file extension is not ".csv", an error message is sent
                    if (file_extension == ".csv") is True:
                        
                        #Uplaoded file stored as a pandas dataframe
                        df_main = pd.read_csv(input_data)
                        df=df_main.copy() #Dropcolumns
                        
                        #Data preprocessing
                        #Amount column is normalized
                        df['amt'] = pt.transform(df[['amt']])

                        #Transaction time is converted to date time object
                        df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'])
                        df['transaction_period'] = df['trans_date_trans_time'].view('int64') // 10**9  # Convert to seconds
                        df.drop(columns=['trans_date_trans_time'], inplace=True)  # Drop original column

                        #Date of birth is converted to date time object
                        df['dob'] = pd.to_datetime(df['dob'])
                        df['new_dob'] = df['dob'].view('int64') // 10**9  # Convert to seconds
                        df.drop(columns=['dob'], inplace=True)  # Drop original column

                        #Encode categorical variables
                        #Encode merchant
                        df['merchant_encoded'] = label_encoder.fit_transform(df['merchant'].fillna('Unknown'))   #Encode merchant
                        df.drop(columns=['merchant'], inplace=True)   #Drop old merchant column

                        #Encode category
                        df['category_encoded'] = label_encoder.fit_transform(df['category'].fillna('Unknown'))
                        df.drop(columns=['category'], inplace=True)

                        #Encode city
                        df['city_encoded'] = label_encoder.fit_transform(df['city'].fillna('Unknown'))
                        df.drop(columns=['city'], inplace=True)        

                        # Scale the features
                        X_scaled = scaler.transform(df)

                         # Convert X_scaled (NumPy array) back to a DataFrame with the original columns
                        X_scaled_df = pd.DataFrame(X_scaled, columns=df.columns)

                        #Position the fields in the correct for the model using .iloc
                        df_new = X_scaled_df.iloc[:, [0, 3, 4, 5, 1, 2]]              
        
                        ##Check for fraud button
                        if st.button("Fraud check"):
                    ##Model prediction
                            
                            #Store models predictions for data in prediction variable
                            prediction=model.predict(df)
                            #Add prediction column to the dataset
                            df["Fraud_Prediction"] = prediction  
                            #Obtain the number of fraud
                            #https://www.geeksforgeeks.org/how-to-extract-the-value-names-and-counts-from-value_counts-in-pandas/
                           
                            fraud_count = df["Fraud_Prediction"].value_counts().get(1, 0)
                            #If number of frauds more than 0 then display error message
                            if fraud_count>0:
                                st.error(f"⚠️ {fraud_count}Fraudulent Transactions Detected! ")
                            #If there are no frauds then a success message displayed
                            else:
                                st.success("✅ No fraudulent transactions")
                                st.success("You can now enter new data to be checked")
                                

                            df_main["Fraud_Prediction"] = prediction  # Add predictions to the uploaded file

        #https://stackoverflow.com/questions/43221208/iterate-over-pandas-dataframe-using-itertuples - How to iterate over a dataframe                                                           
                            #For each row in the uploaded file, add it to the datanbase
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
                        st.error('File type is not csv') #Error message if file type not .csv
                except Exception as e:
                    st.error(f"Error processing file: {e}")  # Show error if reading fails
    ##Logout button
    if st.button("Logout"):
       st.success("Logout successful!")
       st.session_state.authenticated=False   #Session is broken and needs to be reauthenticated

# https://www.tutorialspoint.com/How-to-convert-Python-date-in-JSON-format - How to convert datetime in json format
#https://www.geeksforgeeks.org/how-to-fix-datetime-datetime-not-json-serializable-in-python/ - Serializing datetime

#Store data in sqlite database 
def addTransactions(a,b,c,d,x,y,z):
    conn = sqlite3.connect('fraud.db')  # New connection
    cursor = conn.cursor()  # Create cursor
    cursor.execute(
        """
CREATE TABLE IF NOT EXISTS transaction_z (AMOUNT REAL,TRANSACTION_PERIOD TEXT(50),DOB TEXT(50),MERCHANT TEXT(50),CATEGORY TEXT(50),CITY TEXT(50),FRAUD_PREDICTION INTEGER)
"""
    )
    cursor.execute("INSERT INTO transaction_z VALUES (?,?,?,?,?,?,?)", (a,b,c,d,x,y,z))   #Insert data into database
    conn.commit()

#Store data in supabase
#https://www.youtube.com/watch?v=R7aBgKndPxo - Database connection tutorial - SQlite
def addTransaction(amt,trans_date_trans_time,dob,merchant,category,city,prediction):
   #https://www.geeksforgeeks.org/how-to-fix-datetime-datetime-not-json-serializable-in-python/ - Serializing datetime and transaction time
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
