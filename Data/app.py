import streamlit as st
import pandas as pd
import plotly.express as px
from clean_data import clean_data
from analyze_data import  analytics
from insight import insight
from load_data import load_csv
from filter import filter_data 
from ai_handling import ai
from mapping import mapper
from Validator.duplicated_check import duplicated
from Data.Validator.missing_validation import validation
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s : %(message)s')

#Application Title
st.title('Instagram Campaign Analyzer')

#File Upload
uploaded_file=st.file_uploader("Upload a CSV file of the data",type=["csv"])

#Upload Validation
if uploaded_file:
        if not uploaded_file.name.endswith(".csv"):
            st.error("Invalid Filetype. Use a CSV file")
            st.stop()
        # Load Data
        try:
         df=pd.read_csv(uploaded_file)
        except Exception:
         st.error("Invalid file type or corrupt file")
         st.stop()
         
        #Data Mapping
        if "mapping_confirmed" not in st.session_state:
            st.session_state.mapping_confirmed=False
        if not st.session_state.mapping_confirmed:
         mapping=mapper(df)
         st.header("Please Check the mapping before proceeding with analytics")
         user_mapping=dict()
         with st.expander("Mapping"):
             col1,col2,col3,col4=st.columns([0.2,1.6, 1,0.1])
             with col2:
                 st.subheader("Your Column")
             with col3:
                 st.subheader("Program see's it as")
             for column,alias in mapping.items():
                 with st.container(border=True):
                  col1,col2,col3,col4=st.columns([0.3,1.8, 1,0.3])
                  with col2: 
                      st.write(column)
                      with col3:
                       dropdown_options=[None,"date","platform","campaign_name","ad_set_name","objective","result_type","region","age_group","gender","device","creative_format","cta","budget_inr","spend_inr","impressions","reach","frequency","clicks","ctr_pct","cpc_inr","landing_page_views","add_to_cart","purchases","conversions","conversion_rate_pct","cost_per_conversion_inr","roas","Ignore Column","Custom Column"]
                       user_mapping[column]=st.selectbox("Select Column",options =dropdown_options ,key=f'column_mapper_{column}',index=dropdown_options.index(alias))
         if st.button("Confirm mapping"):
             #Final Mapping
            df.rename(columns=user_mapping,inplace=True)
            duplication=duplicated(df)
            if not duplicated:
                st.error("Duplicated Columns found. Please check the mapping")
            else:
                st.session_state.mapping_confirmed=True
                st.rerun()
            
        #Analytics
        if "analytics_view" not in st.session_state:
            st.session_state.analytics_view = False
            
        if st.session_state.mapping_confirmed:
            if st.button("Show Analytics"):
                st.session_state.analytics_view = True
                st.rerun()
              
        if st.session_state.analytics_view:
        
            # Clean Data
            df,anomalies= clean_data(df)
            

            #Sidebar
            st.sidebar.header("Filters")
            st.sidebar.write("Use the filters below to customize the data displayed.")

            #Campaign Objective Filter
            campaign_objective_filter=st.sidebar.selectbox("Campaign Objective", options=["All"] + list(df['objective'].unique()), key='campaign_filter')

            #Device Filter
            device_filter=st.sidebar.multiselect("Device", options=df['device'].unique(), default=df['device'].unique(), key='device_filter')

            #Gender Filter
            gender_filter=st.sidebar.multiselect("Gender", options=df['gender'].unique(), default=df['gender'].unique(),key='gender_filter')

            #Age Group Filter
            age_group_filter=st.sidebar.multiselect("Age Group", options=df['age_group'].unique(), default=df['age_group'].unique(), key='age_group_filter')

            #Campaign Name Filter
            campaign_name_filter=st.sidebar.multiselect("Campaign Name", options=df['campaign_name'].unique(), default=df['campaign_name'].unique(), key='campaign_name_filter')

            #Date Range Filter
            min_date = df['date'].min()
            max_date = df['date'].max()
            start_date= st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date, key='start_date_filter')
            end_date= st.sidebar.date_input("End Date", value=max_date, min_value=start_date, max_value=max_date, key='end_date_filter')

            # Filter data based on sidebar selection
            df_filtered = filter_data(df, campaign_objective_filter, device_filter, gender_filter, age_group_filter, campaign_name_filter, start_date, end_date)

            # Analyze Data
            basic_kpis, performance_comparison, segmented_analysis, graph_data=analytics(df_filtered)

            # Generate Insights and Recommendations
            kpis,best_performance,under_performance,high_performance,low_ctr_performance,anomalies_insights,recommendations,summary=insight(df_filtered,anomalies,basic_kpis, performance_comparison, segmented_analysis)

            #AI Analysis Container
            with st.container(border=True):
                st.header("Enter your question for AI analysis: ")
                prompt=st.text_area("Prompt", height=100)
                if st.button("Get AI Insights"):
                    if prompt.strip() != "":
                        ai_response = ai(prompt, summary)
                        st.subheader("AI Insights: ")
                        st.write(ai_response)
                    else:
                        st.warning("Please enter a question for AI analysis.")

            # KPIs Container
            with st.container(border=True):
                total_spend = kpis['Total Spend']
                total_impressions = kpis['Total Impressions']
                total_clicks = kpis['Total Clicks']
                total_conversions = kpis['Total Conversions']
                total_reach = kpis['Total Reach']
                avg_ctr = round(kpis['Average CTR'], 2)
                avg_cpc = round(kpis['Average CPC'], 2)
                avg_cpm = round(kpis['Average CPM'], 2)
                conversion_effectiveness = round(kpis['Conversion Effectiveness'], 2)
                st.header("📈 KPIs: ")
                col1,col2,col3=st.columns(3)
                with col1:
                    st.metric(label="Total Spend", value=f"₹{total_spend}")
                with col2:
                    st.metric(label="Total Impressions", value=f"{total_impressions}")
                with col3:
                    st.metric(label="Total Clicks", value=f"{total_clicks}")
                col4,col5,col6=st.columns(3)
                with col4:
                    st.metric(label="Total Conversions", value=f"{total_conversions}")
                with col5:
                    st.metric(label="Total Reach", value=f"{total_reach}")
                with col6:
                    st.metric(label="Average CTR", value=f"{avg_ctr}%")
                col7,col8,col9=st.columns(3)
                with col7:
                    st.metric(label="Average CPC", value=f"₹{avg_cpc}")
                with col8:
                    st.metric(label="Average CPM", value=f"₹{avg_cpm}")
                with col9:
                    st.metric(label="Conversion Effectiveness", value=f"{conversion_effectiveness}%")

            st.divider()

            # Best Performers Container
            with st.container(border=True):
                st.title("Best Performers: ")
                for basis in best_performance:
                    st.header(f"🏆 {basis} Campaign")
                    st.subheader(f"**Campaign Name:** {best_performance[basis]['Name']}")
                    co11, co12, co13 = st.columns(3)
                    with co11:
                        st.metric(label="Conversions", value=f"{best_performance[basis]['Conversions']}")
                    with co12:
                        st.metric(label="CTR (%)", value=f"{best_performance[basis]['CTR'] * 100:.6f}")
                    with co13:
                        st.metric(label="Spend", value=f"₹{best_performance[basis]['Spend']}")
                    with st.expander("View Details", expanded=False):
                     col4, col5, col6 = st.columns(3)
                     with col4:
                        st.metric(label="Clicks", value=f"{best_performance[basis]['Clicks']}")
                     with col5:
                        st.metric(label="Date", value=f"{best_performance[basis]['Date']}")
                     with col6:
                        st.metric(label="Purchases", value=f"{best_performance[basis]['Purchases']}")
                     col7, col8, col9 = st.columns(3)
                     with col7:
                        st.metric(label="CTA", value=f"{best_performance[basis]['CTA']}")
                     with col8:
                        st.metric(label="Impressions", value=f"{best_performance[basis]['Impressions']}")
                     with col9:
                        st.metric(label="Budget", value=f"₹{best_performance[basis]['Budget']}")
                    st.write("\n\n")
            st.divider()


            # Underperformers 
            st.title("Underperformers: ")
            st.write("These campaigns have shown less than average performance in terms of CTR and Conversion Rate. Consider reviewing the campaign creatives, targeting, and budget allocation for these campaigns to improve their performance.")
            with st.expander("View Underperforming Campaigns", expanded=False):
                    st.dataframe(pd.DataFrame(under_performance).T)

            # High Performers
            st.title("High Performers: ")
            st.write("These campaigns have shown exceptional performance in terms of CTR and Conversion Rate. Analyze the campaign strategies, creatives, and targeting to understand what is working well and consider applying similar strategies to other campaigns.")
            with st.expander("View High Performing Campaigns", expanded=False):
                    st.dataframe(pd.DataFrame(high_performance).T)

            # Low CTR Performers
            st.title("Low CTR Performers: ")
            st.write("These campaigns have a low Click-Through Rate (CTR), indicating that the ads may not be resonating well with the audience. Consider reviewing the ad creatives, messaging, and targeting to improve engagement.")
            with st.expander("View Low CTR Campaigns", expanded=False):
                    st.dataframe(pd.DataFrame(low_ctr_performance).T)
            st.divider()


            # Segmented Analysis
            st.title("Segmented Analysis: ")
            st.write("Segmented analysis provides insights into how different audience segments are performing. Analyze the performance of campaigns across various segments such as age group, gender, device, and campaign objective to identify trends and optimize targeting strategies.(These are arranged from highest to lowest CTR)")

            #Gender Segment
            with st.expander("View Gender Segment Analysis", expanded=False):
                st.subheader("Gender Segment Analysis: ")
                st.dataframe(pd.DataFrame(segmented_analysis['gender_segment']).sort_values(by='Segment CTR', ascending=False))

            #Age Group Segment
            with st.expander("View Age Group Segment Analysis", expanded=False):
                st.subheader("Age Group Segment Analysis: ")
                st.dataframe(pd.DataFrame(segmented_analysis['age_segment']).sort_values(by='Segment CTR', ascending=False))

            #Device Segment
            with st.expander("View Device Segment Analysis", expanded=False):
                st.subheader("Device Segment Analysis: ")
                st.dataframe(pd.DataFrame(segmented_analysis['device_segment']).sort_values(by='Segment CTR', ascending=False))

            #Campaign Objective Segment
            with st.expander("View Campaign Objective Segment Analysis", expanded=False):
                st.subheader("Campaign Objective Segment Analysis: ")
                st.dataframe(pd.DataFrame(segmented_analysis['objective_segment']).sort_values(by='Segment CTR', ascending=False))

            st.divider()

            #anomalies insights
            with st.container(border=True):
                    st.title("Anomalies Insights: ")
                    st.write("These insights are derived from the anomalies detected in the dataset. Analyze these insights to understand potential issues in your campaigns.")
                    if anomalies_insights['Spend greater than budget']:
                        with st.expander("Spend Greater than Budget", expanded=False):
                            st.dataframe(pd.DataFrame(anomalies_insights['Spend greater than budget']).T)
                    if anomalies_insights['Conversion without clicks']:
                        with st.expander("Conversion without Clicks", expanded=False):
                            st.dataframe(pd.DataFrame(anomalies_insights['Conversion without clicks']).T)
                    if anomalies_insights['Missing campaign name']:
                        with st.expander("Missing Campaign Name", expanded=False):
                            st.dataframe(pd.DataFrame(anomalies_insights['Missing campaign name']).T)
                    if anomalies_insights['Missing spend inr']:
                        with st.expander("Missing Spend INR", expanded=False):
                            st.dataframe(pd.DataFrame(anomalies_insights['Missing spend inr']).T)
                    if anomalies_insights['Missing impressions']:
                        with st.expander("Missing Impressions", expanded=False):
                            st.dataframe(pd.DataFrame(anomalies_insights['Missing impressions']).T)

            st.divider()

            #Recommendations
            #Budget Reallocation Recommendation
            st.title("Recommendations: ")
            with st.container(border=True):
                st.header("Budget Reallocation Recommendation: ")
                st.subheader('''These are the top 10 performing campaigns based on conversion rate. Consider reallocating budget towards these campaigns to maximize conversions.''')
                if recommendations['Budget Reallocation']: 
                 st.dataframe(pd.DataFrame(recommendations['Budget Reallocation']).T)
                else:
                 st.write("Not enough data to provide budget reallocation recommendations . Consider reducing filters.")

            #Reducing Spend Recommendation
            with st.container(border=True):
             st.header("Reducing Spend Recommendation: ")
             st.subheader('''These are the low performing campaigns based on conversion rate and high spend. Consider reducing spend on these campaigns to optimize budget allocation.''')
             st.subheader("Note: These campaigns have above average spend but below average conversion rates, indicating poor targeting , weak funnel or weak audience fit.")
             if recommendations['Reduce Spend']:
              st.dataframe(pd.DataFrame(recommendations['Reduce Spend']).T)
             else:
                st.write("Not enough data to provide reducing spend recommendations . Consider reducing filters.")

            #Creative Optimization Recommendation
            with st.container(border=True):
                st.header("Creative Optimization Recommendation: ")
                st.write('''These campaigns have low CTR, indicating that the creatives may not be resonating with the audience. 
                        Consider testing new creatives, hooks , ad copy or targeting to improve engagement and CTR.''')
                if recommendations['Creative Optimization']:
                 st.dataframe(pd.DataFrame(recommendations['Creative Optimization']).T)
                else:
                 st.write("Not enough data to provide creative optimization recommendations . Consider reducing filters.")

            #Landing Page Optimization Recommendation
            with st.container(border=True):
                st.header("Landing Page Optimization Recommendation: ")
                st.write('''These campaigns have above average CTR but below average conversion rates, indicating that while the ads are engaging, the landing page experience may be lacking. 
                        Consider optimizing the landing page for better user experience, faster load times, clearer CTAs, and more relevant content to improve conversion rates.''')

                if recommendations['Landing Page Optimization']:
                    st.dataframe(pd.DataFrame(recommendations['Landing Page Optimization']).T)
                else:
                    st.write("Not enough data to provide landing page optimization recommendations . Consider reducing filters.")

            st.divider()
            #Gender Targeting Recommendation
            with st.container(border=True):
                st.header("Gender Targeting Recommendation: ")
                st.write('''Based on the segmented analysis, these are the top performing gender segments.
                        Consider tailoring creatives and messaging to better resonate with these segments or allocating more budget towards them for improved performance.''')
                st.dataframe(recommendations['Gender'])


            #Age Group Targeting Recommendation
            with st.container(border=True):
             st.header("Age Group Targeting Recommendation: ")
             st.write('''Age Group Targeting Recommendation: Based on the segmented analysis, these are the top performing age group segments. "\
                    "Consider tailoring creatives and messaging to better resonate with these segments or allocating more budget towards them for improved performance.''')
             st.dataframe(recommendations['Age'])

            #Device Targeting Recommendation
            with st.container(border=True):
                st.header("Device Targeting Recommendation: ")
                st.write('''Device Targeting Recommendation: Based on the segmented analysis, these are the top performing device segments. "\
                        "Consider tailoring creatives and messaging to better resonate with these segments or allocating more budget towards them for improved performance.''')
                st.dataframe(recommendations['Device'])

            #Campaign Objective Targeting Recommendation
            with st.container(border=True):
                st.header("Campaign Objective Targeting Recommendation: ")
                st.write('''Campaign Objective Targeting Recommendation: Based on the segmented analysis, these are the top performing campaign objective segments. "\
                        "Consider tailoring creatives and messaging to better resonate with these segments or allocating more budget towards them for improved performance.''')
                st.dataframe(recommendations['Campaign'])

            st.divider()
            #Graphical Analysis
            st.title("Graphical Analysis: ")
            #Campaign Objective vs Spend
            figure1=px.bar(graph_data['campaign_name_vs_spend'], x=graph_data['campaign_name_vs_spend'].index, y='spend_inr', title='Campaign Name vs Spend', labels={'y': 'Total Spend (INR)', 'x': 'Campaign Name'},color=graph_data['campaign_name_vs_spend'].index)
            st.plotly_chart(figure1, use_container_width=True)

            #Campaign Name vs Conversion Rate
            figure2=px.bar(graph_data['campaign_name_vs_conversion_rate'], x=graph_data['campaign_name_vs_conversion_rate'].index, y=graph_data['campaign_name_vs_conversion_rate'].values, title='Campaign Name vs Conversion Rate', labels={'y': 'Conversion Rate (%)', 'x': 'Campaign Name'},color=graph_data['campaign_name_vs_conversion_rate'].index)
            st.plotly_chart(figure2, use_container_width=True)

            #Device vs Conversion Rate
            figure3=px.bar(graph_data['device_vs_conversion_rate'], x=graph_data['device_vs_conversion_rate'].index, y=graph_data['device_vs_conversion_rate'].values, title='Device vs Conversion Rate', labels={'y': 'Conversion Rate (%)', 'x': 'Device'},color=graph_data['device_vs_conversion_rate'].index)
            st.plotly_chart(figure3, use_container_width=True)

            #Spend vs Conversion 
            figure4=px.scatter(graph_data['spend_vs_conversions'], x=graph_data['spend_vs_conversions']['spend_inr'], y=graph_data['spend_vs_conversions']['conversions'], title='Spend vs Conversions', labels={'spend_inr': 'Spend (INR)', 'conversions': 'Conversions'},hover_name=graph_data['spend_vs_conversions'].index,size=graph_data['spend_vs_conversions']['conversions'],color=graph_data['spend_vs_conversions']['conversions'])
            st.plotly_chart(figure4, use_container_width=True)

            #Advanced Graphical Analysis
            with st.expander("View Advanced Graphical Analysis", expanded=False):

                #Campaign Name vs CTR
                figure5=px.bar(graph_data['campaign_name_vs_ctr'], x=graph_data['campaign_name_vs_ctr'].index, y=graph_data['campaign_name_vs_ctr'].values, title='Campaign Name vs CTR', labels={'y': 'CTR (%)', 'x': 'Campaign Name'},color=graph_data['campaign_name_vs_ctr'].index)
                st.plotly_chart(figure5, use_container_width=True)

                #Gender vs CTR
                figure6=px.bar(graph_data['gender_vs_ctr'], x=graph_data['gender_vs_ctr'].index, y=graph_data['gender_vs_ctr'].values, title='Gender vs CTR', labels={'y': 'CTR (%)', 'x': 'Gender'},color=graph_data['gender_vs_ctr'].index)
                st.plotly_chart(figure6, use_container_width=True)

                #Gender vs Conversion Rate
                figure7=px.bar(graph_data['gender_vs_conversion_rate'], x=graph_data['gender_vs_conversion_rate'].index, y=graph_data['gender_vs_conversion_rate'].values, title='Gender vs Conversion Rate', labels={'y': 'Conversion Rate (%)', 'x': 'Gender'},color=graph_data['gender_vs_conversion_rate'].index)
                st.plotly_chart(figure7, use_container_width=True)

                #Age Group vs CTR
                figure8=px.bar(graph_data['age_group_vs_ctr'], x=graph_data['age_group_vs_ctr'].index, y=graph_data['age_group_vs_ctr'].values, title='Age Group vs CTR', labels={'y': 'CTR (%)', 'x': 'Age Group'},color=graph_data['age_group_vs_ctr'].index)
                st.plotly_chart(figure8, use_container_width=True)

                #Age Group vs Conversion Rate
                figure9=px.bar(graph_data['age_group_vs_conversion_rate'], x=graph_data['age_group_vs_conversion_rate'].index, y=graph_data['age_group_vs_conversion_rate'].values, title='Age Group vs Conversion Rate', labels={'y': 'Conversion Rate (%)', 'x': 'Age Group'},color=graph_data['age_group_vs_conversion_rate'].index)
                st.plotly_chart(figure9, use_container_width=True)

                #Spend Over Time
                figure10=px.line(x=graph_data['spend_over_time'].index, y=graph_data['spend_over_time'].values, title='Spend Over Time', labels={'x': 'Date', 'y': 'Total Spend (INR)'}, markers=True)
                st.plotly_chart(figure10, use_container_width=True)

                #Clicks Over Time
                figure11=px.line(x=graph_data['clicks_over_time'].index, y=graph_data['clicks_over_time'].values, title='Clicks Over Time', labels={'x': 'Date', 'y': 'Total Clicks'}, markers=True)
                st.plotly_chart(figure11, use_container_width=True)

                #Conversions Over Time
                figure12=px.line(x=graph_data['conversions_over_time'].index, y=graph_data['conversions_over_time'].values, title='Conversions Over Time', labels={'x': 'Date', 'y': 'Total Conversions'}, markers=True)
                st.plotly_chart(figure12, use_container_width=True)

                #CTR Over Time
                figure13=px.line(x=graph_data['ctr_over_time'].index, y=graph_data['ctr_over_time'].values, title='CTR Over Time', labels={'x': 'Date', 'y': 'CTR (%)'}, markers=True)
                st.plotly_chart(figure13, use_container_width=True)

                #Spend Distribution by Objective
                figure14=px.pie(values=graph_data['spend_distribution_by_objective'].values, names=graph_data['spend_distribution_by_objective'].index, title='Spend Distribution by Objective', labels={'names': 'Objective'})
                st.plotly_chart(figure14, use_container_width=True)

                #Conversions Distribution by Objective
                figure15=px.pie(values=graph_data['conversions_distribution_by_objective'].values, names=graph_data['conversions_distribution_by_objective'].index, title='Conversions Distribution by Objective', labels={'names': 'Objective'})
                st.plotly_chart(figure15, use_container_width=True)

                #Spend vs CTR
                figure16=px.scatter(graph_data['spend_vs_ctr'], x=graph_data['spend_vs_ctr']['spend_inr'], y=graph_data['spend_vs_ctr']['ctr_pct'], title='Spend vs CTR', labels={'spend_inr': 'Spend (INR)', 'ctr_pct': 'CTR (%)'}, hover_name=graph_data['spend_vs_ctr'].index, size=graph_data['spend_vs_ctr']['spend_inr'], color=graph_data['spend_vs_ctr']['ctr_pct'])
                st.plotly_chart(figure16, use_container_width=True)

                #Clicks vs Conversions
                figure17=px.scatter(graph_data['clicks_vs_conversions'], x=graph_data['clicks_vs_conversions']['clicks'], y=graph_data['clicks_vs_conversions']['conversions'], title='Clicks vs Conversions', labels={'clicks': 'Total Clicks', 'conversions': 'Total Conversions'}, hover_name=graph_data['clicks_vs_conversions'].index, size=graph_data['clicks_vs_conversions']['conversions'], color=graph_data['clicks_vs_conversions']['conversions'])
                st.plotly_chart(figure17, use_container_width=True)

                #Impressions vs Clicks
                figure18=px.scatter(graph_data['impressions_vs_clicks'], x=graph_data['impressions_vs_clicks']['impressions'], y=graph_data['impressions_vs_clicks']['clicks'], title='Impressions vs Clicks', labels={'impressions': 'Total Impressions', 'clicks': 'Total Clicks'}, hover_name=graph_data['impressions_vs_clicks'].index, size=graph_data['impressions_vs_clicks']['clicks'], color=graph_data['impressions_vs_clicks']['clicks'])
                st.plotly_chart(figure18, use_container_width=True)
else:
    st.header("Please Upload a File")
