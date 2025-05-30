import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px


## Homepage
def home():
    st.set_page_config(layout="wide") # column widths set below are based on the layout of the page

    st.markdown('<h1 style="text-align: center;font-size:80px;color:#bad7d9;font-family:Georgia">Fraud Guard</h1>', unsafe_allow_html=True,) #Header
    st.divider()
    st.sidebar.success("Select a page from above.") #Sidebar

    st.markdown('<div style="color:#bad7d9;font-size:25px;font-family:roboto">Credit card fraud within the next 5 years will cause many global losses. A study revealed that as many as 80% of the US credit cards currently in use have been compromised and the fraud rate keeps on increasing</div>',unsafe_allow_html=True)
    st.write("##")
   
    st.markdown('<div style="color:#bad7d9;font-size:25px;font-family:roboto">Want to check for fraud? Click on the button below</div>',unsafe_allow_html=True)
   
   #Button to fraudcheck login page
    st.link_button("Check for fraud", "https://fraudguard1.streamlit.app/FraudCheck")

    col1,col2,col3=st.columns([1, 2, 1])
    
    ##Graph showing credit card fraud over the years
    with col2:    
        st.write("##")
        st.markdown('<div style="color:#bad7d9;font-size:27px;font-family:roboto;text-align: center"><b>Credit card fraud over the years</b></div>',unsafe_allow_html=True)
        #https://streamlit.io/components - Adding third party components
        st.components.v1.iframe("https://public.flourish.studio/visualisation/22210475/", height=500)
        st.markdown("*https://www.merchantsavvy.co.uk/payment-fraud-statistics/*")
    
    st.markdown('<div style="color:#bad7d9;font-size:25px;font-family:roboto">ML-based fraud detection solutions are modern methods which are used to track patterns and prevent abnormal transactions from taking place.</div>',unsafe_allow_html=True)
    st.divider()

    st.markdown('<h1 style="text-align: center;font-size:60px;color:#bad7d9;font-family:Georgia">About us</h1>', unsafe_allow_html=True,)
    st.markdown('<div style="text-align:center;color:#bad7d9;font-size:25px;font-family:roboto">Fraud Guard is a Real-Time fraud prevention solution for organizations battling fraud</div>',unsafe_allow_html=True)
    st.write("##")

    #Consists of the "about us" section
    col4,col5=st.columns(2)
    col6,col7=st.columns(2)
  
    with col4:   #Accurate fraud prediction logo and text
        st.image("pages/arrow.jpg",width=400)
        st.write("https://uk.pinterest.com/pin/327496204170575857/")
        st.markdown('<div style="color:#bad7d9;font-size:29px;font-family:Georgia"><b>Accurate fraud detection</b></div>',unsafe_allow_html=True)
        st.markdown('<div style="color:#bad7d9;font-size:25px;font-family:roboto">Catch fraud with high precision and recall</div>',unsafe_allow_html=True)
    
    with col5:   #real time logo and text
        st.image("pages/Bell.jpg",width=265)   
        st.write("https://uk.pinterest.com/pin/612348880588536701/")
        st.markdown('<div style="color:#bad7d9;font-size:29px;font-family:Georgia"><b>Act on real cases, in real time</b></div>',unsafe_allow_html=True)
        st.markdown('<div style="color:#bad7d9;font-size:25px;font-family:roboto">Prevent and mitigate transaction fraud in real time by having real time alerts when there is a fraud detected</div>',unsafe_allow_html=True)
   
    with col6:   #Scalalble and 24/7 uptime logo and text
        st.image("pages/some.jpg",width=460)
        st.write("https://uk.pinterest.com/pin/624311567070400876/")
        st.markdown('<div style="color:#bad7d9;font-size:29px;font-family:Georgia"><b>Scalable & 24/7 uptime</b></div>',unsafe_allow_html=True)
        st.markdown('<div style="color:#bad7d9;font-size:25px;font-family:roboto">Can handle large volumes of data, working 24/7 with no downtime</div>',unsafe_allow_html=True)
    
    with col7:  #Implement and configure logo and text
        st.image("pages/inter.jpg",width=400)
        st.write("https://insights.grcglobalgroup.com/data-interoperability/")
        st.markdown('<div style="color:#bad7d9;font-size:29px;font-family:Georgia"><b>Implement & configure with ease</b></div>',unsafe_allow_html=True)
        st.markdown('<div style="color:#bad7d9;font-size:25px;font-family:roboto">Interoperable with any system so that you dont have to start your detection from scratch</div>',unsafe_allow_html=True)

home()



