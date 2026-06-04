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
    graph_data = dict()
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

    #Graph Data 
    try:

        #Campaign Name vs Spend
        graph_data['campaign_name_vs_spend'] = df.groupby('campaign_name')['spend_inr'].sum()


        #Campaign Objective vs Conversion Rate
        total_conversions = df.groupby('campaign_name')['conversions'].sum()
        total_clicks = df.groupby('campaign_name')['clicks'].sum()
        graph_data['campaign_name_vs_conversion_rate'] = (total_conversions / total_clicks) * 100

        #Device vs Conversion Rate
        total_conversions = df.groupby('device')['conversions'].sum()
        total_clicks = df.groupby('device')['clicks'].sum()
        graph_data['device_vs_conversion_rate'] = (total_conversions / total_clicks) * 100

        #Spend vs Conversions
        graph_data['spend_vs_conversions'] = df.groupby('campaign_name').agg({'spend_inr': 'sum', 'conversions': 'sum'})

        #Advanced Analysis 

        #Campaign name vs CTR
        total_clicks = df.groupby('campaign_name')['clicks'].sum()
        total_impressions = df.groupby('campaign_name')['impressions'].sum()
        graph_data['campaign_name_vs_ctr'] = (total_clicks / total_impressions) * 100

        #Campaign name vs CPC
        total_spend = df.groupby('campaign_name')['spend_inr'].sum()
        total_clicks = df.groupby('campaign_name')['clicks'].sum()
        graph_data['campaign_name_vs_cpc'] = total_spend / total_clicks

        #Objective vs Spend
        graph_data['objective_vs_spend'] = df.groupby('objective')['spend_inr'].sum()

        #Objective vs Conversion Rate
        total_conversions = df.groupby('objective')['conversions'].sum()
        total_clicks = df.groupby('objective')['clicks'].sum()
        graph_data['objective_vs_conversion_rate'] = (total_conversions / total_clicks) * 100

        #Device vs CTR
        total_clicks = df.groupby('device')['clicks'].sum()
        total_impressions = df.groupby('device')['impressions'].sum()
        graph_data['device_vs_ctr'] = (total_clicks / total_impressions) * 100

        #Device vs CPC
        total_spend = df.groupby('device')['spend_inr'].sum()
        total_clicks = df.groupby('device')['clicks'].sum()
        graph_data['device_vs_cpc'] = total_spend / total_clicks

        #Gender vs CTR
        total_clicks = df.groupby('gender')['clicks'].sum()
        total_impressions = df.groupby('gender')['impressions'].sum()
        graph_data['gender_vs_ctr'] = (total_clicks / total_impressions) * 100

        #Gender vs Conversion Rate
        total_conversions = df.groupby('gender')['conversions'].sum()
        total_clicks = df.groupby('gender')['clicks'].sum()
        graph_data['gender_vs_conversion_rate'] = (total_conversions / total_clicks) * 100

        #Age Group vs CTR
        total_clicks = df.groupby('age_group')['clicks'].sum()
        total_impressions = df.groupby('age_group')['impressions'].sum()
        graph_data['age_group_vs_ctr'] = (total_clicks / total_impressions) * 100

        #Age Group vs Conversion Rate
        total_conversions = df.groupby('age_group')['conversions'].sum()
        total_clicks = df.groupby('age_group')['clicks'].sum()
        graph_data['age_group_vs_conversion_rate'] = (total_conversions / total_clicks) * 100

        #Spend Over Time
        df_sorted = df.sort_values('date')
        graph_data['spend_over_time'] = df_sorted.groupby('date')['spend_inr'].sum()

        #Clicks Over Time
        graph_data['clicks_over_time'] = df_sorted.groupby('date')['clicks'].sum()

        #Conversions Over Time
        graph_data['conversions_over_time'] = df_sorted.groupby('date')['conversions'].sum()

        #CTR Over Time
        daily_clicks = df_sorted.groupby('date')['clicks'].sum()
        daily_impressions = df_sorted.groupby('date')['impressions'].sum()
        graph_data['ctr_over_time'] = (daily_clicks / daily_impressions) * 100

        #Spend Distribution by Objective
        graph_data['spend_distribution_by_objective'] = df.groupby('objective')['spend_inr'].sum()

        #Conversions Distribution by Objective
        graph_data['conversions_distribution_by_objective'] = df.groupby('objective')['conversions'].sum()

        #Spend vs CTR
        graph_data['spend_vs_ctr'] = df.groupby('campaign_name').agg({'spend_inr': 'sum', 'ctr_pct': 'median'})

        #Clicks vs Conversions
        graph_data['clicks_vs_conversions'] = df.groupby('campaign_name').agg({'clicks': 'sum', 'conversions': 'sum'})

        #Impressions vs Clicks
        graph_data['impressions_vs_clicks'] = df.groupby('campaign_name').agg({'impressions': 'sum', 'clicks': 'sum'})

        
    except Exception as e:
        print("Error in file analyze_data.py in graph data: ", e)



    return basic_kpis, performance_comparison, segmented_analysis, graph_data
