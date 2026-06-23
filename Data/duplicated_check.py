import pandas as pd
def duplicated(df):
    ignore=[None,"Ignore Column","Custom Column"]
    columns=list(df.columns)
    columns=pd.Series(columns)
    columns=columns[~columns.isin(ignore)]
    duplicate_columns=columns[columns.duplicated()]
    result=duplicate_columns.empty
    return result
    