import pandas as pd
def mapper(df):
    mapping=dict()
    
    #Column Handling
    columns=list(df.columns.str.strip().str.lower().str.replace(" ","_"))
    df.columns=columns
    aliasis={"date": ["date", "day", "report_date"],
    "campaign_name": ["campaign_name", "campaign"],
    "ad_set_name": ["ad_set_name", "ad_set", "adgroup"],
    "gender": ["gender", "sex"],
    "age_group": ["age_group", "age_range"],
    "device": ["device", "device_type"],
    "cta": ["cta", "call_to_action"],
    "budget_inr": ["budget", "campaign_budget", "daily_budget"],
    "spend_inr": ["spend", "amount_spent", "ad_spend"],
    "clicks": ["clicks", "link_clicks"],
    "reach": ["reach", "unique_reach"],
    "frequency": ["frequency"],
    "purchases": ["purchases", "purchase", "orders"],
    "roas": ["roas", "return_on_ad_spend"]}
    for column in df.columns:
     mapping[column]=None
     for alias,value in aliasis.items():
        if column in value:
            mapping[column]=alias
            break
            
    return mapping