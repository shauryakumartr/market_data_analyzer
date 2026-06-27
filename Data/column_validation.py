import pandas as pd 
def validation(df):
    columns=pd.Series(df.columns)
    mandatory=pd.Series(['date','budget_inr','spend_inr','impressions','reach','clicks','conversions'])
    optional=pd.Series(['platform', 'campaign_name', 'ad_set_name', 'objective','result_type', 'region', 'age_group', 'gender', 'device','creative_format','add_to_cart', 'purchases'])
    derieved=pd.Series(['ctr_pct', 'cpc_inr','conversion_rate_pct', 'cost_per_conversion_inr', 'roas'])
    result=dict()
    
    #Checking for mandatory columns
    missing_mandatory=set(mandatory)-set(columns)
    if 
    
    