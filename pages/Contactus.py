
import streamlit as st
import smtplib
import random
import os
import time
import datetime

from email_validator import validate_email, EmailNotValidError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from captcha.image import ImageCaptcha
from io import BytesIO
from PIL import Image
from streamlit_js_eval import streamlit_js_eval
#https://github.com/jlnetosci/streamlit-contact-form/blob/main/pages/contact-form.py  - Contact form code help
## Page configuration options
st.set_page_config(layout="wide") # column widths set below are dependent on the layout being set to wide

## Load secrets.toml variables
options = os.getenv("OPTIONS")
server = os.getenv("SERVER")
port = os.getenv("PORT")
u = os.getenv("U")
secret = os.getenv("SECRET")
recipient = os.getenv("RECIPIENT")

## Functions
def generate_captcha():
    options = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"  # Define valid characters

    captcha_text = "".join(random.choices(options, k=6)) # options is a string of characters that can be included in the CAPTCHA. It may be as simple or as complex as you wish. 
    image = ImageCaptcha(width=400, height=100).generate(captcha_text)
    return captcha_text, image

## Generate CAPTCHA
if 'captcha_text' not in st.session_state:
    
    st.session_state.captcha_text = generate_captcha()

captcha_text, captcha_image = st.session_state.captcha_text

## Contact Form
st.markdown('<h1 style="text-align: center;font-size:80px;color:#bad7d9;font-family:Georgia">✉️ Contact Form</h1>', unsafe_allow_html=True,)
col1, col2, col3, col4 =  st.columns([3, 0.25, 1, 0.25]) # column widths for a balanced distribution of elements in the page

captcha_input = None # initiate CAPTCHA

## CAPTCHA
with col3: # right side of the layout
    st.markdown('<p style="text-align: justify; font-size: 12px;color:#bad7d9">CAPTCHAs are active to prevent automated submissions. <br> Thank you for your understanding.</p>', unsafe_allow_html=True) # warning for user.
    captcha_placeholder = st.empty()
    captcha_placeholder.image(captcha_image, use_container_width=True)

    if st.button("Refresh", type="secondary", use_container_width=True): # option to refresh CAPTCHA without refreshing the page
        st.session_state.captcha_text = generate_captcha()
        captcha_text, captcha_image = st.session_state.captcha_text
        captcha_placeholder.image(captcha_image, use_container_width=True)

    captcha_input = st.text_input("Enter the CAPTCHA") # box to insert CAPTCHA

## Contact form
with col1: # left side of the layout
    name = st.text_input("**Your name***", value=st.session_state.get('name', ''), key='name') # input widget for contact name

    email = st.text_input("**Your email***", value=st.session_state.get('email', ''), key='email') # input widget for contact email
    message = st.text_area("**Your message***", value=st.session_state.get('message', ''), key='message') # input widget for message

    st.markdown('<p style="font-size: 13px;color:#bad7d9">*Required fields</p>', unsafe_allow_html=True) # indication to user that both fields must be filled

    if st.button("Send", type="primary"):
        if not email or not message:
            st.error("Please fill out all required fields.") # error for any blank field
        else:
            try:
                # Robust email validation
                valid = validate_email(email, check_deliverability=True)

                # Check CAPTCHA
                if captcha_input.upper() == captcha_text:

                    st.info("""This would have been a message sent successfully!  
                    For more information on activating the contact form, please check the [documentation](https://github.com/jlnetosci/streamlit-contact-form).""") # Please delete this info box if you have the contact form setup correctly.

                    # Generate a new captcha to prevent button spamming.
                    st.session_state.captcha_text = generate_captcha()
                    captcha_text, captcha_image = st.session_state.captcha_text
                    # Update the displayed captcha image
                    captcha_placeholder.image(captcha_image, use_column_width=True)

                    time.sleep(3)
                    streamlit_js_eval(js_expressions="parent.window.location.reload()")

                else:
                    st.error("Text does not match the CAPTCHA.") # error to the user in case CAPTCHA does not match input

            except EmailNotValidError as e:
                st.error(f"Invalid email address. {e}") # error in case any of the email validation checks have not passed

