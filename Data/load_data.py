import pandas as pd
import  re
def load_csv(path):
    try:
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()  # Removes hidden spaces from headers
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
        print(type(df['date']))
        return df
    except Exception as e:
        print(f"An error occurred while loading the CSV file: {e}")
        return None
