import streamlit as st
import re 
import sqlite3
import os
import bcrypt
from supabase import create_client

#https://www.youtube.com/watch?v=dU7GwCOgvNY - How to use supabase database
#Url and key for supabase database connection
url="https://gywtlivqrvxgttetymwh.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd5d3RsaXZxcnZ4Z3R0ZXR5bXdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQzMDQxMTAsImV4cCI6MjA1OTg4MDExMH0.1cL2AKAwyA_exgRE3qGh17KbYXa-gPDl93w-kjvAyAw"
#Create client function to create a connection
supabase=create_client(url,key)
 
#Function for hashing password
# https://www.geeksforgeeks.org/how-to-hash-passwords-in-python/ - Hashing password tutorial 
def hashPassword(new_password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')  
    return hashed_password

##Signup
def signup():
    st.markdown('<h1 style="text-align: center;font-size:80px;color:#bad7d9;font-family:Georgia">Signup</h1>', unsafe_allow_html=True,)

    st.write("Please submit your account details. We will verify and email you back shortly")
    #Store data in account details array
    account_details=[]
    #Characters restriction and requirement for passwords and emails
    pattern_password = "^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$"
    pattern_email="^[a-zA-Z0-9._%+-]+@[a-zA0-9.-]+\.[a-zA-Z]{2,}$"

    #Data fields for creating users
    first_name= st.text_input("Enter your first name: ", value="", max_chars=20, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder="Enter your first name", disabled=False, label_visibility="visible")
    last_name= st.text_input("Enter your last name: ", value="", max_chars=20, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder="Enter your first name", disabled=False, label_visibility="visible")
    contact_details= st.text_input("Enter your contact number: ", value="", max_chars=13, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder="Enter your first name", disabled=False, label_visibility="visible")
    company= st.text_input("Enter the name of your company: ", value="", max_chars=30, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder="Enter your first name", disabled=False, label_visibility="visible")  
    email=st.text_input("Enter your email: ", value="", max_chars=20, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder="Type here", disabled=False, label_visibility="visible")
    new_password=st.text_input("Enter your password: ", value="", max_chars=25, key=None, type="password", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder="Password must contain: 8+ characters, a special character, a capital or simple letter and number", disabled=False, label_visibility="visible")
    confirm_password=st.text_input("Enter your password again: ", value="", max_chars=25, key=None, type="password", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder="Password must contain: 8+ characters, a special character, a capital or simple letter and number", disabled=False, label_visibility="visible")

    #https://stackoverflow.com/questions/2990654/how-to-test-a-regex-password-in-python
    validation_password=re.findall(pattern_password,new_password)
    #https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/   
    validation_email=re.findall(pattern_email,email)
    
    #Consent box
    accept_data=st.checkbox("I hereby allow Fraud Guard to store my data")
    #If consented
    if accept_data:
        st.button("Submit details")  #Data is submited

        if st.button:
                if (validation_email):  
                    #Validation for length of password     
                    if len(new_password)<8:
                        st.error("Password is too short. Must be 8 characters long")

                    #Validation for contact details - needs to be numeric
                    elif not contact_details.isdigit():
                        st.error("Contact number must contain only digits (0–9).")
                    #Validation for password - Both entered passwords have to be the same    
                    elif (validation_password):   
                        if new_password == confirm_password:
                            #If all details correct then stored in new "account_detail" array
                            if all([first_name, last_name, contact_details,company, email, new_password]):
                                account_detail = {
                                "first_name": first_name,
                                "last_name": last_name,
                                "contact_details":contact_details,
                                "company": company,
                                "email": email,
                                "password": new_password
                                 }
                                #Success message stating details have been submitted
                                st.success("Details have been submitted. You will receive a verification email shortly")
                                
                                hashed_password = hashPassword(new_password)  # Hash password before storing
                                
                                #Add signup details to supabase database
                                addInfo(first_name,last_name,contact_details,company,email,hashed_password)
                                #Add each signup details to "account_details" array
                                account_details.append(account_detail)
                                st.link_button("Go back to homepage", "https://fraudguard1.streamlit.app/")

                            #Validation to check if all fields have been filled
                            else:
                                st.error("All fields are required. Please fill in all the fields.")
                        #Error message if passwords entered do not match
                        else:
                            st.error("Passwords do not match. Please try again.")
                    #Password conditions
                    else:
                        st.error("Password should contain 'atleast': a special character [@#$%^&+=]")
                        st.error("An Uppercase letter: A-Z")
                        st.error("A Lowercase letter:a-z")
                        st.error("A number:0-9")
                #Error message if email not valid
                else:
                    st.error("Email is not valid. Please enter a valid email address")

##Supabase function
#https://www.youtube.com/watch?v=dU7GwCOgvNY - How to use supabase database
def addInfo(first_name, last_name, contact_details, company, email, hashed_password):
    # Insert data into Supabase table
    data = {
        "first_name": first_name,
        "last_name": last_name,
        "contact_details": contact_details,
        "company": company,
        "email": email,
        "password": hashed_password
      
    }
    #Insert command
    response = supabase.table("registrations").insert(data).execute()
    
signup()
