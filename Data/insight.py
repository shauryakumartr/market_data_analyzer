import pandas as pd

def best_performers(performance_comparison,df,basis):
    try:
     print(f'''\nCampaign with  {basis} -> Name: {df.loc[performance_comparison[f'{basis}'], 'campaign_name']}
                              Date: {df.loc[performance_comparison[f'{basis}'], 'date']}
                              CTR: {df.loc[performance_comparison[f'{basis}'], 'ctr_pct']}
                              CTA: {df.loc[performance_comparison[f'{basis}'], 'cta']}
                              Budget: {df.loc[performance_comparison[f'{basis}'], 'budget_inr']}
                              Spend: {df.loc[performance_comparison[f'{basis}'], 'spend_inr']}
                              Impressions: {df.loc[performance_comparison[f'{basis}'], 'impressions']}
                              Clicks: {df.loc[performance_comparison[f'{basis}'], 'clicks']}
                              Purchases: {df.loc[performance_comparison[f'{basis}'], 'purchases']}
                              Conversions: {df.loc[performance_comparison[f'{basis}'], 'conversions']}''')
    except Exception as e:
        print(f"Error in file insight.py in best performers function: ", e)
    
def performers(indexes,df,type):
    try:
        print(f"\n{type} Campaigns:")
        for campaign in indexes:
             print(f'''\nName: {df.loc[campaign, 'campaign_name']}
             Date: {df.loc[campaign, 'date']}
             CTR: {df.loc[campaign, 'ctr_pct']}
             CTA: {df.loc[campaign, 'cta']}
             Budget: {df.loc[campaign, 'budget_inr']}
             Spend: {df.loc[campaign, 'spend_inr']}
             Impressions: {df.loc[campaign, 'impressions']}
             Clicks: {df.loc[campaign, 'clicks']}
             Purchases: {df.loc[campaign, 'purchases']}
             Conversions: {df.loc[campaign, 'conversions']}''') 
    except Exception as e:
        print(f"Error in file insight.py in performers function: ", e)

def segmented(segmented_analysis,type):
     try:
          segment=segmented_analysis[f'{type}']
          print(f'''\n   Segment CTR: {segment.sort_values(by='Segment CTR',ascending=False).head(1)['Segment CTR']}
   Segment CPC: {segment.sort_values(by='Segment CTR',ascending=False).head(1)['Segment CPC']}
   Total Spend: {segment.sort_values(by='Segment CTR',ascending=False).head(1)['Total Spend']}
   Total Impressions: {segment.sort_values(by='Segment CTR',ascending=False).head(1)['Total Impressions']}
   Total Clicks: {segment.sort_values(by='Segment CTR',ascending=False).head(1)['Total Clicks']}
   Total Conversions: {segment.sort_values(by='Segment CTR',ascending=False).head(1)['Total Conversions']}
   Conversion Rate: {segment.sort_values(by='Segment CTR',ascending=False).head(1)['Segment Conversion Rate']}''')
     except Exception as e:
         print("Error in file insight.py in segmented analysis function: ", e)
    
def insight(df,anomalies,basic_kpis, performance_comparison, segmented_analysis):

    #Performance Summary
    try:
          print("Performance Summary:")
          print(f"\nTotal Spend: {basic_kpis['total_spend']}")
          print(f"\nTotal Impressions: {basic_kpis['total_impressions']}")
          print(f"\nTotal Clicks: {basic_kpis['total_clicks']}")
          print(f"\nTotal Conversions: {basic_kpis['total_conversions']}")
          print(f"\nTotal Reach: {basic_kpis['total_reach']}")
          print(f"\nAverage CTR: {basic_kpis['avg_ctr']}")
          print(f"\nAverage CPC: {basic_kpis['avg_cpc']}")
          print(f"\nAverage CPM: {basic_kpis['avg_cpm']}")
          print(f"\nConversion Effectiveness: {basic_kpis['avg_conversion_rate']}%")
    except Exception as e:
        print("Error in file insight.py in performance summary: ", e)
   

    #Best Performers
    
    try:
         print("\nBest Performers:")
         best_performers(performance_comparison,df,'Best CTR')
         best_performers(performance_comparison,df,'Highest conversion campaign')
    except Exception as e:
         print("Error in file insight.py in best performers: ", e)


    #Underperformers
    try:
         performers(performance_comparison['Low performing campaigns'],df,'Low Performing') 
    except Exception as e:
         print("Error in file insight.py in underperformers: ", e)
         
    #High Performers
    try:
         performers(performance_comparison['High performing campaigns'],df,'High Performing')
    except Exception as e:
            print("Error in file insight.py in high performers: ", e)

    #Low CTR Performers
    try:
         performers(performance_comparison['Low CTR campaigns'],df,'Low CTR')
    except Exception as e:
            print("Error in file insight.py in low CTR performers: ", e)

    #Segmented Analysis
    print("\nSegmented Analysis:")

    #Gender
    try:
         print("\nGender Segment Analysis:")
         segmented(segmented_analysis,'gender_segment')
    except Exception as e:
         print("Error in file insight.py in segmented analysis for gender: ", e)

     #Age Group
    try:
          print("\nAge Group Segment Analysis:")
          segmented(segmented_analysis,'age_segment')
    except Exception as e:
          print("Error in file insight.py in segmented analysis for age group: ", e) 

     #Device
    try:
            print("\nDevice Segment Analysis:") 
            segmented(segmented_analysis,'device_segment')
    except Exception as e:
            print("Error in file insight.py in segmented analysis for device: ", e)    

     #Campaign Objective
    try:
            print("\nCampaign Objective Segment Analysis:")
            segmented(segmented_analysis,'objective_segment')
    except Exception as e:
            print("Error in file insight.py in segmented analysis for campaign objective: ", e)
     
     #Anomalies
    print("\nAnomalies:")

     #Spend greater than budget
    try:
         print("\nSpend greater than budget:")
         spend_greater_than_budget_indexes=anomalies['Spend greater than budget']
         for index in spend_greater_than_budget_indexes:
              print(f'''\nName: {df.loc[index, 'campaign_name']}
     objective: {df.loc[index, 'objective']}
     Date: {df.loc[index, 'date']}
     Budget: {df.loc[index, 'budget_inr']}
     Spend: {df.loc[index, 'spend_inr']}''')
    except Exception as e:
           print("Error in file insight.py in anomalies for spend greater than budget: ", e)


     #Conversion without clicks
    try:
         print("\nConversion without clicks:")
         conversion_without_clicks_indexes=anomalies['Conversion without clicks']
         for index in conversion_without_clicks_indexes:
              print(f'''\nName: {df.loc[index, 'campaign_name']}
     objective: {df.loc[index, 'objective']}
     Date: {df.loc[index, 'date']}
     Conversion: {df.loc[index, 'conversions']}
     Clicks: {df.loc[index, 'clicks']}''')
    except Exception as e:
             print("Error in file insight.py in anomalies for conversion without clicks: ", e)

     #Missing campaign name
    try:
           print("\nMissing campaign name:")
           missing_campaign_name_indexes=anomalies['Missing campaign name']
           for index in missing_campaign_name_indexes:
                 print(f'''\n Name : N/A
      objective: {df.loc[index, 'objective']}
      Date: {df.loc[index, 'date']}
      Budget: {df.loc[index, 'budget_inr']}
      Spend: {df.loc[index, 'spend_inr']}''')
    except Exception as e:
                print("Error in file insight.py in anomalies for missing campaign name: ", e)

     #Missing spend inr
    try:
           print("\nMissing spend inr:")
           missing_spend_inr_indexes=anomalies['Missing spend inr']
           for index in missing_spend_inr_indexes:
                 print(f'''\nName: {df.loc[index, 'campaign_name']}
      objective: {df.loc[index, 'objective']}
      Date: {df.loc[index, 'date']}
      Budget: {df.loc[index, 'budget_inr']}
      Spend: N/A''')
      
    except Exception as e:
          print("Error in file insight.py in anomalies for missing spend inr: ", e)

     #Missing impressions
    try:
               print("\nMissing impressions:")
               missing_impressions_indexes=anomalies['Missing impressions']
               for index in missing_impressions_indexes:
                    print(f'''\nName: {df.loc[index, 'campaign_name']}
          objective: {df.loc[index, 'objective']}
          Date: {df.loc[index, 'date']}
          Budget: {df.loc[index, 'budget_inr']}
          Spend: {df.loc[index, 'spend_inr']}
          Impressions: N/A''')
    except Exception as e:
          print("Error in file insight.py in anomalies for missing impressions: ", e)

     #Recommendations
    print("\nRecommendations:")

    #Budget Reallocation Recommendation
    try:
           i=0
           print('''\nBudget Reallocation Recommendation: These are the top performing campaigns based on conversion rate. 
           Consider reallocating budget towards these campaigns to maximize conversions.''')
           high_performing_campaigns=performance_comparison['High performing campaigns']
           for campaign in high_performing_campaigns:
                 print(f'''\nName: {df.loc[campaign, 'campaign_name']}
      objective: {df.loc[campaign, 'objective']}
      Date: {df.loc[campaign, 'date']}
      Budget: {df.loc[campaign, 'budget_inr']}
      Spend: {df.loc[campaign, 'spend_inr']}
      CTR: {df.loc[campaign, 'ctr_pct']}
      Conversion Rate: {df.loc[campaign, 'conversion_rate_pct']}''')
                 i+=1
                 if i>=10:  # Limiting to top 10 recommendations
                    break
    except Exception as e:
            print("Error in file insight.py in budget reallocation recommendation: ", e)

     #Reduce Spend Recommendation
    try:
               i=0
               print('''\nReduce Spend Recommendation: These are the low performing campaigns based on conversion rate and high spend. 
               Consider reducing spend on these campaigns to optimize budget allocation.''')
               print('''\nNote: These campaigns have above average spend but below average conversion rates, 
                     indicating poor targeting , weak funnel or weak audience fit.''')
               low_performing_campaigns=performance_comparison['Low performing campaigns']
               for campaign in low_performing_campaigns:
                    print(f'''\nName: {df.loc[campaign, 'campaign_name']}
          objective: {df.loc[campaign, 'objective']}
          Date: {df.loc[campaign, 'date']}
          Budget: {df.loc[campaign, 'budget_inr']}
          Spend: {df.loc[campaign, 'spend_inr']}
          CTR: {df.loc[campaign, 'ctr_pct']}
          Conversion Rate: {df.loc[campaign, 'conversion_rate_pct']}''')
                    i+=1
                    if i>=10:  # Limiting to top 10 recommendations
                        break
    except Exception as e:
            print("Error in file insight.py in reduce spend recommendation: ", e)
     

     #Creative Optimization Recommendation
    try:
          i=0
          print('''\nCreative Optimization Recommendation: These campaigns have low CTR, indicating that the creatives may not be resonating with the audience. 
          Consider testing new creatives, hooks , ad copy or targeting to improve engagement and CTR.''')
          low_ctr_campaigns=performance_comparison['Low CTR campaigns']
          for campaign in low_ctr_campaigns:
                print(f'''\nName: {df.loc[campaign, 'campaign_name']}
          objective: {df.loc[campaign, 'objective']}
          Date: {df.loc[campaign, 'date']}
          Budget: {df.loc[campaign, 'budget_inr']}
          Spend: {df.loc[campaign, 'spend_inr']}
          CTR: {df.loc[campaign, 'ctr_pct']}
          Conversion Rate: {df.loc[campaign, 'conversion_rate_pct']}''')
                i+=1
                if i>=10:  # Limiting to top 10 recommendations
                    break
    except Exception as e:
            print("Error in file insight.py in creative optimization recommendation: ", e)
     
     #Landing Page Optimization Recommendation
    try:
          i=0
          print('''\nLanding Page Optimization Recommendation: These campaigns have above average CTR but below average conversion rates, indicating that while the ads are engaging, the landing page experience may be lacking. 
          Consider optimizing the landing page for better user experience, faster load times, clearer CTAs, and more relevant content to improve conversion rates.''')
          low_landing_page_conversion_campaigns=performance_comparison['Low Landing page conversion campaign']
          for campaign in low_landing_page_conversion_campaigns:
                print(f'''\nName: {df.loc[campaign, 'campaign_name']}
          objective: {df.loc[campaign, 'objective']}
          Date: {df.loc[campaign, 'date']}
          Budget: {df.loc[campaign, 'budget_inr']}
          Spend: {df.loc[campaign, 'spend_inr']}
          CTR: {df.loc[campaign, 'ctr_pct']}
          Conversion Rate: {df.loc[campaign, 'conversion_rate_pct']}''')
                i+=1
                if i>=10:  # Limiting to top 10 recommendations
                    break
    except Exception as e:
            print("Error in file insight.py in landing page optimization recommendation: ", e)

     #Gender Targeting Recommendation
    try:
          print("\nGender Targeting Recommendation: Based on the segmented analysis, these are the top performing gender segments. " \
          "Consider tailoring creatives and messaging to better resonate with these segments or allocating more budget towards them for improved performance.")
          gender_segment=segmented_analysis['gender_segment']
          index=gender_segment.sort_values(by='Segment CTR',ascending=False).head(1).index[0]
          print(f'''\nGender: {index}
          Segment CTR: {gender_segment.loc[index, 'Segment CTR']}
          Total impressions: {gender_segment.loc[index, 'Total Impressions']}
          Total clicks: {gender_segment.loc[index, 'Total Clicks']}
          Segment CPC: {gender_segment.loc[index, 'Segment CPC']}
          Total Spend: {gender_segment.loc[index, 'Total Spend']}''')
    except Exception as e:
            print("Error in file insight.py in gender targeting recommendation: ", e)
          
     #Age Group Targeting Recommendation
    try:
          print("\nAge Group Targeting Recommendation: Based on the segmented analysis, these are the top performing age group segments. "\
          "Consider tailoring creatives and messaging to better resonate with these segments or allocating more budget towards them for improved performance.")
          age_segment=segmented_analysis['age_segment']
          index=age_segment.sort_values(by='Segment CTR',ascending=False).head(1).index[0]
          print(f'''\nAge Group: {index}
          Segment CTR: {age_segment.loc[index, 'Segment CTR']}
          Total impressions: {age_segment.loc[index, 'Total Impressions']}
          Total clicks: {age_segment.loc[index, 'Total Clicks']}
          Segment CPC: {age_segment.loc[index, 'Segment CPC']}
          Total Spend: {age_segment.loc[index, 'Total Spend']}''')
    except Exception as e:
            print("Error in file insight.py in age group targeting recommendation: ", e)

     #Device Targeting Recommendation
    try:
          print("\nDevice Targeting Recommendation: Based on the segmented analysis, these are the top performing device segments. "\
          "Consider tailoring creatives and messaging to better resonate with these segments or allocating more budget towards them for improved performance.")
          device_segment=segmented_analysis['device_segment']
          index=device_segment.sort_values(by='Segment CTR',ascending=False).head(1).index[0]
          print(f'''\nDevice: {index}
          Segment CTR: {device_segment.loc[index, 'Segment CTR']}
          Total impressions: {device_segment.loc[index, 'Total Impressions']}
          Total clicks: {device_segment.loc[index, 'Total Clicks']}
          Segment CPC: {device_segment.loc[index, 'Segment CPC']}
          Total Spend: {device_segment.loc[index, 'Total Spend']}''') 
    except Exception as e:
               print("Error in file insight.py in device targeting recommendation: ", e)

     #Campaign Objective Targeting Recommendation
    try:
          print("\nCampaign Objective Targeting Recommendation: Based on the segmented analysis, these are the top performing campaign objective segments. "\
          "Consider tailoring creatives and messaging to better resonate with these segments or allocating more budget towards them for improved performance.")
          objective_segment=segmented_analysis['objective_segment']
          index=objective_segment.sort_values(by='Segment CTR',ascending=False).head(1).index[0]
          print(f'''\nCampaign Objective: {index}
          Segment CTR: {objective_segment.loc[index, 'Segment CTR']}
          Total impressions: {objective_segment.loc[index, 'Total Impressions']}
          Total clicks: {objective_segment.loc[index, 'Total Clicks']}
          Segment CPC: {objective_segment.loc[index, 'Segment CPC']}
          Total Spend: {objective_segment.loc[index, 'Total Spend']}''')
    except Exception as e:
            print("Error in file insight.py in campaign objective targeting recommendation: ", e)
