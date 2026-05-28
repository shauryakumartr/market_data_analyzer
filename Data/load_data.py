import pandas as pd
import  re
def load_csv(path):
    try:
        df = pd.read_csv('instagram_campaign_csv_analyzer_dataset.csv')
        df.columns = df.columns.str.strip()  # Removes hidden spaces from headers
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
        return df
    except Exception as e:
        print(f"An error occurred while loading the CSV file: {e}")
        return None
