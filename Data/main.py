import pandas as pd
from clean_data import clean_data
from analyze_data import  analytics
from insight import insight
from load_data import load_csv
from filter import filter_data
def main():
    try:
        # Load Data
       df=load_csv('instagram_campaign_csv_analyzer_dataset_new.csv')
        # Clean Data
       df,anomalies = clean_data(df)

       campaign_objective_filter = "Sales"  

       df_filtered = filter_data(df, campaign_objective_filter)

        # Analyze Data
       basic_kpis, performance_comparison, segmented_analysis, graph_data=analytics(df_filtered)

       # Generate Insights and Recommendations
       kpis,best_performance,under_performance,high_performance,low_ctr_performance,anomalies_insights,recommendations=insight(df_filtered,anomalies,basic_kpis, performance_comparison, segmented_analysis)
       print(anomalies_insights.keys())
    except Exception as e:
        print("Error in file main.py: ", e)

if __name__ == "__main__":
    main()