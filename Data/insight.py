import pandas as pd
from itertools import islice
def best_performers(performance_comparison,df,best_performance,basis):
    try:
     temp={'Name': df.loc[performance_comparison[f'{basis}'], 'campaign_name'],
                              'Date': df.loc[performance_comparison[f'{basis}'], 'date'],
                              'CTR': df.loc[performance_comparison[f'{basis}'], 'ctr_pct'],
                              'CTA': df.loc[performance_comparison[f'{basis}'], 'cta'],
                              'Budget': df.loc[performance_comparison[f'{basis}'], 'budget_inr'],
                              'Spend': df.loc[performance_comparison[f'{basis}'], 'spend_inr'],
                              'Impressions': df.loc[performance_comparison[f'{basis}'], 'impressions'],
                              'Clicks': df.loc[performance_comparison[f'{basis}'], 'clicks'],
                              'Purchases': df.loc[performance_comparison[f'{basis}'], 'purchases'],
                              'Conversions': df.loc[performance_comparison[f'{basis}'], 'conversions']}
     best_performance[f'{basis}']=temp
    except Exception as e:
        print(f"Error in file insight.py in best performers function: ", e)
    
def performers(indexes,df,performance):
    try:
        for index in indexes:
             performance[index]={
             'Campaign Name': df.loc[index, 'campaign_name'],
             'Date': df.loc[index, 'date'],
             'CTR': round(df.loc[index, 'ctr_pct']*100,2),
             'CTA': df.loc[index, 'cta'],
             'Budget': f'₹ {df.loc[index, 'budget_inr']}',
             'Spend': f'₹ {df.loc[index, 'spend_inr']}',
             'Impressions': df.loc[index, 'impressions'],
             'Clicks': df.loc[index, 'clicks'],
             'Purchases': df.loc[index, 'purchases'],
             'Conversions': df.loc[index, 'conversions']} 
    except Exception as e:
        print(f"Error in file insight.py in performers function: ", e)
def insight(df,anomalies,basic_kpis, performance_comparison, segmented_analysis):
    kpis = dict()
    best_performance = dict()
    under_performance= dict()
    high_performance= dict()
    low_ctr_performance= dict()
    anomalies_insights = dict()
    recommendations = dict()
    summary = dict() #Summary of all insights and recommendations for using in ai context.


    #Performance KPIs
    try:
          kpis = {
    "Total Spend": basic_kpis['total_spend'],
    "Total Impressions": basic_kpis['total_impressions'],
    "Total Clicks": basic_kpis['total_clicks'],
    "Total Conversions": basic_kpis['total_conversions'],
    "Total Reach": basic_kpis['total_reach'],
    "Average CTR": round(basic_kpis['avg_ctr'],2),
    "Average CPC": round(basic_kpis['avg_cpc'],2),
    "Average CPM": round(basic_kpis['avg_cpm'],2),
    "Conversion Effectiveness": round(float(basic_kpis['avg_conversion_rate']),2)
                   }
          
    except Exception as e:
        print("Error in file insight.py in performance summary: ", e)
   

    #Best Performers
    
    try:
         best_performers(performance_comparison,df,best_performance,'Best CTR')
         best_performers(performance_comparison,df,best_performance,'Highest conversion campaign')
         
    except Exception as e:
         print("Error in file insight.py in best performers: ", e)


    #Underperformers
    try:
         performers(performance_comparison['Low performing campaigns'],df,under_performance)

    except Exception as e:
         print("Error in file insight.py in underperformers: ", e)
         
    #High Performers
    try:
         performers(performance_comparison['High performing campaigns'],df,high_performance)
    except Exception as e:
            print("Error in file insight.py in high performers: ", e)

    #Low CTR Performers
    try:
         performers(performance_comparison['Low CTR campaigns'],df,low_ctr_performance)
    except Exception as e:
            print("Error in file insight.py in low CTR performers: ", e)



     #Anomalies
     #Spend greater than budget
    try:
         
         spend_greater_than_budget_indexes=anomalies['Spend greater than budget']
         temp=dict()
         temp2=dict()
         for index in spend_greater_than_budget_indexes:
              if index in df.index:
                temp[index]={'Name': df.loc[index, 'campaign_name'],
                    'objective': df.loc[index, 'objective'],
                    'Date': df.loc[index, 'date'],
                    'Budget': f'₹ {df.loc[index, 'budget_inr']}',
                    'Spend': df.loc[index, 'spend_inr']}
                
                temp2[index]=f"Name {df.loc[index, 'campaign_name']} ,objective{df.loc[index, 'objective']},date{df.loc[index, 'date']},budget{df.loc[index, 'budget_inr']},spend{df.loc[index, 'spend_inr']}"
         anomalies_insights['Spend greater than budget']=temp
         summary["Spend Greater than Budget anomalie"]=temp2
    except Exception as e:
           print("Error in file insight.py in anomalies for spend greater than budget: ", e)


     #Conversion without clicks
    try:
         conversion_without_clicks_indexes=anomalies['Conversion without clicks']
         temp=dict()
         temp2=dict()
         for index in conversion_without_clicks_indexes:
                 if index in df.index:
                  temp[index]={'Name': df.loc[index, 'campaign_name'],
                    'objective': df.loc[index, 'objective'],
                    'Date': df.loc[index, 'date'],
                    'Budget': df.loc[index, 'budget_inr'],
                    'Spend': df.loc[index, 'spend_inr']}
                  
                 temp2[index]=f"Name {df.loc[index, 'campaign_name']} ,objective{df.loc[index, 'objective']},date{df.loc[index, 'date']},budget{df.loc[index, 'budget_inr']},spend{df.loc[index, 'spend_inr']}"

         anomalies_insights['Conversion without clicks']=temp
         summary["Conversion Without click anomalie"]=temp2
    except Exception as e:
             print("Error in file insight.py in anomalies for conversion without clicks: ", e)

     #Missing campaign name
    try:
           missing_campaign_name_indexes=anomalies['Missing campaign name']
           temp=dict()
           temp2=dict()
           for index in missing_campaign_name_indexes:
                 if index in df.index:
                  temp[index]={'Name': 'N/A',
                    'objective': df.loc[index, 'objective'],
                    'Date': df.loc[index, 'date'],
                    'Budget': df.loc[index, 'budget_inr'],
                    'Spend': df.loc[index, 'spend_inr']}
                  
                  temp2[index]=f"Name {df.loc[index, 'campaign_name']} ,objective{df.loc[index, 'objective']},date{df.loc[index, 'date']},budget{df.loc[index, 'budget_inr']},spend{df.loc[index, 'spend_inr']}"
           anomalies_insights['Missing campaign name']=temp
           summary["Missing campaign name anomalie"]=temp2
    except Exception as e:
                print("Error in file insight.py in anomalies for missing campaign name: ", e)

     #Missing spend inr
    try:
           missing_spend_inr_indexes=anomalies['Missing spend inr']
           temp=dict()
           temp2=dict()
           for index in missing_spend_inr_indexes:
                 if index in df.index:
                  temp[index]={'Name': df.loc[index, 'campaign_name'],
                    'objective': df.loc[index, 'objective'],
                    'Date': df.loc[index, 'date'],
                    'Budget': df.loc[index, 'budget_inr'],
                    'Spend': 'N/A'}

                 temp2[index]=f"Name {df.loc[index, 'campaign_name']} ,objective{df.loc[index, 'objective']},date{df.loc[index, 'date']},budget{df.loc[index, 'budget_inr']},spend{df.loc[index, 'spend_inr']}"
           anomalies_insights['Missing spend inr']=temp
           summary["Missing inr anomalie"]=temp2
    except Exception as e:
          print("Error in file insight.py in anomalies for missing spend inr: ", e)

     #Missing impressions
    try:
               missing_impressions_indexes=anomalies['Missing impressions']
               temp=dict()
               temp2=dict()
               for index in missing_impressions_indexes:
                 if index in df.index:
                  temp[index]={'Name': df.loc[index, 'campaign_name'],
                          'objective': df.loc[index, 'objective'],
                          'Date': df.loc[index, 'date'],
                          'Budget': df.loc[index, 'budget_inr'],
                          'Spend': df.loc[index, 'spend_inr'],
                          'Impressions': 'N/A'}

                  temp2[index]=f"Name {df.loc[index, 'campaign_name']} ,objective{df.loc[index, 'objective']},date{df.loc[index, 'date']},budget{df.loc[index, 'budget_inr']},spend{df.loc[index, 'spend_inr']}"
               anomalies_insights['Missing impressions']=temp
               summary["Missing impression anomalie"]=temp2
    except Exception as e:
          print("Error in file insight.py in anomalies for missing impressions: ", e)

     #Recommendations

    #Budget Reallocation Recommendation
    try:
           
           high_performing_campaigns=performance_comparison['High performing campaigns']
           i=0
           temp=dict()
           temp2=dict()
           for campaign in high_performing_campaigns:
                 if campaign in df.index:
                  temp[campaign]={'Name': df.loc[campaign, 'campaign_name'],
                                 'objective': df.loc[campaign, 'objective'],
                                 'Date': df.loc[campaign, 'date'],
                                 'Budget': df.loc[campaign, 'budget_inr'],
                                 'Spend': df.loc[campaign, 'spend_inr'],
                                 'CTR': df.loc[campaign, 'ctr_pct']*100,
                                 'Conversion Rate': df.loc[campaign, 'conversion_rate_pct']*100}
                  
                  temp2[campaign]={'Name': df.loc[campaign, 'campaign_name'],
                                 'Date': df.loc[campaign, 'date'],
                                 'Spend': df.loc[campaign, 'spend_inr'],
                                 'CTR': df.loc[campaign, 'ctr_pct']*100,
                                 'Conversion Rate': df.loc[campaign, 'conversion_rate_pct']*100}
                 i+=1
                 if i>=10:  # Limiting to top 10 recommendations
                    break
           recommendations['Budget Reallocation']=temp
           summary['Budget Reallocation']=(pd.DataFrame(temp2).T)
    except Exception as e:
            print("Error in file insight.py in budget reallocation recommendation: ", e)

     #Reduce Spend Recommendation
    try:
               low_performing_campaigns=performance_comparison['Low performing campaigns']
               temp=dict()
               temp2=dict()
               i=0
               for campaign in low_performing_campaigns:
                    if campaign in df.index:
                     temp[campaign]={'Name': df.loc[campaign, 'campaign_name'],
                                     'objective': df.loc[campaign, 'objective'],
                                     'Date': df.loc[campaign, 'date'],
                                     'Budget': df.loc[campaign, 'budget_inr'],
                                     'Spend': df.loc[campaign, 'spend_inr'],
                                     'CTR': df.loc[campaign, 'ctr_pct']*100,
                                     'Conversion Rate': df.loc[campaign, 'conversion_rate_pct']*100}
                     
                     temp2[campaign]={'Name': df.loc[campaign, 'campaign_name'],
                                     'Date': df.loc[campaign, 'date'],
                                     'Spend': df.loc[campaign, 'spend_inr'],
                                     'CTR': df.loc[campaign, 'ctr_pct']*100,
                                     'Conversion Rate': df.loc[campaign, 'conversion_rate_pct']*100}
                    i+=1
                    if i>=10:  # Limiting to top 10 recommendations
                        break
               recommendations['Reduce Spend']=temp
               summary['Reduce Spend']=(pd.DataFrame(temp2).T)
    except Exception as e:
            print("Error in file insight.py in reduce spend recommendation: ", e)
     

     #Creative Optimization Recommendation
    try:
          low_ctr_campaigns=performance_comparison['Low CTR campaigns']
          i=0
          temp=dict()
          temp2=dict()
          for campaign in low_ctr_campaigns:
                if campaign in df.index:
                     temp[campaign]={'Name': df.loc[campaign, 'campaign_name'],
                                     'objective': df.loc[campaign, 'objective'],
                                     'Date': df.loc[campaign, 'date'],
                                     'Budget': df.loc[campaign, 'budget_inr'],
                                     'Spend': df.loc[campaign, 'spend_inr'],
                                     'CTR': df.loc[campaign, 'ctr_pct']*100,
                                     'Conversion Rate': df.loc[campaign, 'conversion_rate_pct']*100}
                     
                     temp[campaign]={'Name': df.loc[campaign, 'campaign_name'],
                                     'Date': df.loc[campaign, 'date'],
                                     'Spend': df.loc[campaign, 'spend_inr'],
                                     'CTR': df.loc[campaign, 'ctr_pct']*100,
                                     'Conversion Rate': df.loc[campaign, 'conversion_rate_pct']*100}
                i+=1
                if i>=10:  # Limiting to top 10 recommendations
                    break
          recommendations['Creative Optimization']=temp
          summary['Creative Optimization']=(pd.DataFrame(temp2).T)
    except Exception as e:
            print("Error in file insight.py in creative optimization recommendation: ", e)
     
     #Landing Page Optimization Recommendation
    try:
          low_landing_page_conversion_campaigns=performance_comparison['Low Landing page conversion campaign']
          temp=dict()
          temp2=dict()
          i=0
          for campaign in low_landing_page_conversion_campaigns:
                if campaign in df.index:
                     temp[campaign]={'Name': df.loc[campaign, 'campaign_name'],
                                     'objective': df.loc[campaign, 'objective'],
                                     'Date': df.loc[campaign, 'date'],
                                     'Budget': df.loc[campaign, 'budget_inr'],
                                     'Spend': df.loc[campaign, 'spend_inr'],
                                     'CTR': df.loc[campaign, 'ctr_pct']*100,
                                     'Conversion Rate': df.loc[campaign, 'conversion_rate_pct']*100}
                     
                     temp2[campaign]={'Name': df.loc[campaign, 'campaign_name'],
                                     'Date': df.loc[campaign, 'date'],
                                     'Spend': df.loc[campaign, 'spend_inr'],
                                     'CTR': df.loc[campaign, 'ctr_pct']*100,
                                     'Conversion Rate': df.loc[campaign, 'conversion_rate_pct']*100}
                i+=1
                if i>=10:  # Limiting to top 10 recommendations
                    break
          recommendations['Landing Page Optimization']=temp
          summary['Landing Page Optimization']=(pd.DataFrame(temp2).T)
    except Exception as e:
            print("Error in file insight.py in landing page optimization recommendation: ", e)

     #Gender Targeting Recommendation
    try:
          gender_segment=segmented_analysis['gender_segment']
          index=gender_segment.sort_values(by='Segment CTR',ascending=False).head(1).index[0]
          recommendations['Gender']={'Name':index,
                                     'Segment CTR': gender_segment.loc[index, 'Segment CTR'],
                                     'Total Impressions': gender_segment.loc[index, 'Total Impressions'],
                                     'Total Clicks': gender_segment.loc[index, 'Total Clicks'],
                                     'Segment CPC': gender_segment.loc[index, 'Segment CPC'],
                                     'Total Spend': gender_segment.loc[index, 'Total Spend']}
          
    except Exception as e:
            print("Error in file insight.py in gender targeting recommendation: ", e)
          
     #Age Group Targeting Recommendation
    try:
          age_segment=segmented_analysis['age_segment']
          index=age_segment.sort_values(by='Segment CTR',ascending=False).head(1).index[0]
          recommendations['Age']={'Name':index,
                                     'Segment CTR': age_segment.loc[index, 'Segment CTR'],
                                     'Total Impressions': age_segment.loc[index, 'Total Impressions'],
                                     'Total Clicks': age_segment.loc[index, 'Total Clicks'],
                                     'Segment CPC': age_segment.loc[index, 'Segment CPC'],
                                     'Total Spend': age_segment.loc[index, 'Total Spend']}
    except Exception as e:
            print("Error in file insight.py in age group targeting recommendation: ", e)

     #Device Targeting Recommendation
    try:
          device_segment=segmented_analysis['device_segment']
          index=device_segment.sort_values(by='Segment CTR',ascending=False).head(1).index[0]
          recommendations['Device']={'Name':index,
                                     'Segment CTR': device_segment.loc[index, 'Segment CTR'],
                                     'Total Impressions': device_segment.loc[index, 'Total Impressions'],
                                     'Total Clicks': device_segment.loc[index, 'Total Clicks'],
                                     'Segment CPC': device_segment.loc[index, 'Segment CPC'],
                                     'Total Spend': device_segment.loc[index, 'Total Spend']} 
    except Exception as e:
               print("Error in file insight.py in device targeting recommendation: ", e)

     #Campaign Objective Targeting Recommendation
    try:
          objective_segment=segmented_analysis['objective_segment']
          index=objective_segment.sort_values(by='Segment CTR',ascending=False).head(1).index[0]
          recommendations['Campaign']={'Name':index,
                                     'Segment CTR': objective_segment.loc[index, 'Segment CTR'],
                                     'Total Impressions': objective_segment.loc[index, 'Total Impressions'],
                                     'Total Clicks': objective_segment.loc[index, 'Total Clicks'],
                                     'Segment CPC': objective_segment.loc[index, 'Segment CPC'],
                                     'Total Spend': objective_segment.loc[index, 'Total Spend']}
    except Exception as e:
            print("Error in file insight.py in campaign objective targeting recommendation: ", e)
     
     #Summary

     #KPIS
    summary['KPIs']=kpis
    
    #Best Performers
    for campaign in best_performance:
      summary[campaign]={'Name':best_performance[campaign]['Name'],
                         'CTR':best_performance[campaign]['CTR'],
                         'Date':best_performance[campaign]['Date'],
                         'Spend':best_performance[campaign]['Spend']}
      
     #Segmented Analysis
    for analysis in segmented_analysis:
     analysis_df=segmented_analysis[analysis].loc[:,['Total Spend','Total Clicks','Total Impressions','Total Conversions']]
     summary[analysis]=analysis_df


          
    return kpis,best_performance,under_performance,high_performance,low_ctr_performance,anomalies_insights,recommendations,summary