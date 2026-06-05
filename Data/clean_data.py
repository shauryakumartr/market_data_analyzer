import pandas as pd
import numpy as np
from datetime import  datetime as dt
def clean_data(df):
    anomalies = dict()
    #percentage columns
    df['ctr_pct']=df['clicks']/df['impressions']*100
    df['conversion_rate_pct']=df['conversions']/df['clicks']*100
    percentage_cols = ['ctr_pct', 'conversion_rate_pct']
    for col in percentage_cols:
        try:
            df[col]=df[col]/100
        except Exception as e:
            print(f"Error in converting {col} from percentage: ", e)
    # Remove Duplicate Rows
    df.drop_duplicates(inplace=True)
    #Cheking anomalies in the data

      # Date
    try:
        filt = df['date'].apply(lambda x: pd.to_datetime(x).date()) > dt.today().date()
        df=df[~filt]
    except Exception as e:
        print("Error in file clean_data.py in date filtering: ", e)

      #Numerical columns
    try:
        filt=((df['spend_inr']<0) | (df['budget_inr']<0 )| (df['clicks'] > df['impressions'] )| (df['conversions'] > df['clicks']) | (df['reach'] > df['impressions'] )|(df['ctr_pct']>1) |(df['conversion_rate_pct']>1)|(df['clicks']<0) |(df['impressions']<0) |(df['conversions']<0))
        df=df[~filt]
    except Exception as e:
        print("Error in file clean_data.py in other filtering: ", e)

      #Business Logics Anomalies
    try:
        #spend should not be greater than budget
        spend_inr=df['spend_inr']
        budget_inr=df['budget_inr']
        filt=(spend_inr>budget_inr)
        indexes=df[filt].index
        anomalies['Spend greater than budget']=indexes

        #Conversion exist but clicks are zero
        clicks=df['clicks']
        conversions=df['conversions']
        filt=(conversions>0) & (clicks==0)
        indexes=df[filt].index
        anomalies['Conversion without clicks']=indexes

        #Missing Fields
        for field in df['campaign_name']:
            if pd.isna(field):
                df['campaign_name'].fillna('Unknown', inplace=True)
            indexes=df[df['campaign_name']=='Unknown'].index
            anomalies['Missing campaign name']=indexes
        
        for field in df['spend_inr']:
            if pd.isna(field):
                df['spend_inr'].fillna(0, inplace=True)
            indexes=df[df['spend_inr']==0].index
            anomalies['Missing spend inr']=indexes
        
        for field in df['impressions']:
            if pd.isna(field):
                df['impressions'].fillna(0, inplace=True)
            indexes=df[df['impressions']==0].index
            anomalies['Missing impressions']=indexes
    except Exception as e:
        print("Error in file clean_data.py in business logic filtering: ", e)

    return df, anomalies