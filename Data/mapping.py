import pandas as pd
def mapping(df,map):
        mapping=dict()
        columns=list(df.columns.str.strip().str.lower().str.replace(" ","_"))
        df.columns=columns
        aliasis=map
        for alias,value in aliasis.items():
         for column in df.columns:
            if column in value:
                df.rename(columns={column:alias},inplace=True)
                mapping[column]=alias
        return df 
            