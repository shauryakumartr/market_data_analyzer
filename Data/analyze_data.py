import pandas as pd

#Renaming columns for better understanding and readability
def rename_columns(df):
    try :
        df.rename(columns={'spend_inr':'Total Spend','impressions':'Total Impressions','clicks':'Total Clicks'
                           ,'conversions':'Total Conversions','ctr_pct':'Average CTR','cpc_inr':'Avergae CPC'
                           ,'conversion_rate_pct':'Average Conversion Rate','CTR':'Segment CTR','CPC':'Segment CPC'
                           ,'conversion_rate':'Segment Conversion Rate'},inplace=True)
        return df
    except Exception as e:
        print("Error in file analyze_data.py in rename_columns: ", e)

#Metrices calculator
def calculate_metrics(df):
    try:
        df=df.assign(CTR= (df['clicks'] / df['impressions']),
                        CPC=(df['spend_inr']/df['clicks']),
                      conversion_rate= (df['conversions']/df['clicks']))
        return df
    except Exception as e:
        print("Error in file analyze_data.py in calculate_metrics: ", e)

#Data Segmenter
def segmenter(df, segment_column):
    try:
        segmented_df=df.groupby(segment_column,as_index=True).agg({'spend_inr':'sum' ,'impressions':'sum'
                                            ,'clicks':'sum','conversions':'sum',
                                            'ctr_pct':'median','cpc_inr':'median',
                                            'conversion_rate_pct':'median'})
        return segmented_df
    except Exception as e:  
        print("Error in file analyze_data.py in segmenter: ", e)

def analytics(df):
    basic_kpis = dict()
    performance_comparison = dict()
    segmented_analysis = dict()
    # Basic Analytics KPIs
    try:
        basic_kpis['total_spend'] = df['spend_inr'].sum()
        basic_kpis['total_impressions'] = df['impressions'].sum()
        basic_kpis['total_clicks'] = df['clicks'].sum()
        basic_kpis['total_conversions'] = df['conversions'].sum()
        basic_kpis['total_reach'] = df['reach'].sum()
        basic_kpis['avg_ctr'] = (basic_kpis['total_clicks'] / basic_kpis['total_impressions'])*100 if basic_kpis['total_impressions'] > 0 else 0
        basic_kpis['avg_cpc'] = (basic_kpis['total_spend'] / basic_kpis['total_clicks']) if basic_kpis['total_clicks'] > 0 else 0
        basic_kpis['avg_cpm'] = basic_kpis['total_spend'] / basic_kpis['total_impressions'] * 1000 if basic_kpis['total_impressions'] > 0 else 0
        basic_kpis['avg_conversion_rate'] = (basic_kpis['total_conversions'] / basic_kpis['total_clicks'])*100 if basic_kpis['total_clicks'] > 0 else 0
    except Exception as e:
        print("Error in file analyze_data.py in analytics: ", e)

    #Performance Comparison
    try:
        #Best CTR
        performance_comparison['Best CTR']=df.loc[:,'ctr_pct'].idxmax()

        #Worst CTR
        performance_comparison['Worst CTR']=df.loc[:,'ctr_pct'].idxmin()

        #Best Conversion Rate
        performance_comparison['Highest conversion campaign']=df.loc[:,'conversion_rate_pct'].idxmax()

        
        #Most expensive CPC
        performance_comparison['Most expensive CPC']=df.loc[:,'cpc_inr'].idxmax()
       
        #Highest Spend  
        performance_comparison['highest spend']=df.loc[:,'spend_inr'].idxmax()
       
        #Low performing campaigns
        filt= (df['spend_inr']>df['spend_inr'].mean())  & (df['conversion_rate_pct']<df['conversion_rate_pct'].mean())
        performance_comparison['Low performing campaigns']=df[filt].index

        #High performing campaigns
        filt= (df['spend_inr']<df['spend_inr'].mean())  & (df['conversion_rate_pct']>df['conversion_rate_pct'].mean())
        performance_comparison['High performing campaigns']=df[filt].index

        #Low CTR campaigns
        filt= (df['ctr_pct']<df['ctr_pct'].mean())
        performance_comparison['Low CTR campaigns']=df[filt].index

        #Low Landing Page Conversions
        filt= (df['conversions']<df['conversions'].mean())  & (df['ctr_pct']>df['ctr_pct'].mean())
        performance_comparison['Low Landing page conversion campaign']=df[filt].index

    except Exception as e:
        print("Error in file analyze_data.py in performance comparison: ", e)

       

        #Segmented Analysis

       
    try:
        #AGE GROUP
        age_segment=segmenter(df,'age_group')
        age_segment=calculate_metrics(age_segment)
        rename_columns(age_segment)
        segmented_analysis['age_segment']=age_segment
        
        #GENDER
        gender_segment=segmenter(df,'gender')
        gender_segment=calculate_metrics(gender_segment)
        rename_columns(gender_segment)
        segmented_analysis['gender_segment']=gender_segment
        
        #Device
        device_segment=segmenter(df,'device')
        device_segment=calculate_metrics(device_segment)
        rename_columns(device_segment)
        segmented_analysis['device_segment']=device_segment
        
        #Campaign Objective
        objective_segment=segmenter(df,'objective')
        objective_segment=calculate_metrics(objective_segment)
        rename_columns(objective_segment)
        segmented_analysis['objective_segment']=objective_segment
      
    except Exception as e:
        print("Error in file analyze_data.py in segmented analysis: ", e)
        
    return basic_kpis, performance_comparison, segmented_analysis
