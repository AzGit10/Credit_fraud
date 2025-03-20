import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import pandas as pd
import plotly.express as px
import numpy as np


def loadTransaction():
    conn = sqlite3.connect('fraud.db')  # New connection
    cursor = conn.cursor()  # Create cursor
    cursor.execute("SELECT * FROM transaction_z")
    results=cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df_transactions = pd.DataFrame(results, columns=columns)
    return df_transactions

st.markdown('<h1 style="text-align: center;font-size:80px;color:#bad7d9;font-family:Georgia">Dashboard</h1>', unsafe_allow_html=True,)
st.divider()
#https://www.youtube.com/watch?v=Sb0A9i6d320&list=PLHgX2IExbFovFg4DI0_b3EWyIGk-oGRzq
df_transactions=loadTransaction()

total_fraud_transactions=(df_transactions["FRAUD_PREDICTION"]==1).sum()
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

col3,col4=st.columns(2)

#https://www.youtube.com/watch?v=Sb0A9i6d320&list=PLHgX2IExbFovFg4DI0_b3EWyIGk-oGRzq
with col3:
    st.markdown('<h2 style="text-align: center;font-size:30px;color:#bad7d9;font-family:Georgia">Average transaction by fraud</h2>', unsafe_allow_html=True,)

    # Group by 'is_fraud' and calculate the mean transaction amount
    amt_fraud=(
         df_transactions.groupby('FRAUD_PREDICTION')['AMOUNT'].mean().reset_index()
)
# Plot the result
    fig_amt_fraud=px.bar(
        amt_fraud,
        x="AMOUNT",
        y="FRAUD_PREDICTION",
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

    sns.countplot(x='FRAUD_PREDICTION', data=df_transactions)
    ax.set_title('')
    ax.set_xlabel('Is Fraud')
    ax.set_ylabel('Count')
    st.plotly_chart(fig)