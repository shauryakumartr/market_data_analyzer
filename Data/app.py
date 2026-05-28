from clean_data import clean_data
from load_data import load_csv
import streamlit as st
st.title('Instagram Campaign Analyzer')
# Load Data
df=load_csv('instagram_campaign_csv_analyzer_dataset.csv')
        # Clean Data
df,anomalies = clean_data(df)
st.dataframe(df)
