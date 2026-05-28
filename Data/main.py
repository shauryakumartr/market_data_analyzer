import pandas as pd
from clean_data import clean_data
from analyze_data import  analytics
from insight import insight
from load_data import load_csv
def main():
    try:
        # Load Data
       df=load_csv('instagram_campaign_csv_analyzer_dataset.csv')
        # Clean Data
       df,anomalies = clean_data(df)

        # Analyze Data
       basic_kpis, performance_comparison, segmented_analysis = analytics(df)

        # Generate Insights
       insight(df,anomalies,basic_kpis, performance_comparison, segmented_analysis)
    except Exception as e:
        print("Error in file main.py: ", e)

if __name__ == "__main__":
    main()