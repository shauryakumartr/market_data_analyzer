import pandas as pd
import logging
def duplicated(df: pd.DataFrame) -> bool:
    logging.info('Checking for duplicated columns in dataframe after mapping')
    ignore=[None,"Ignore Column","Custom Column"]
    columns=list(df.columns)
    columns=pd.Series(columns)
    columns=columns[~columns.isin(ignore)]
    duplicate_columns=columns[columns.duplicated()]
    duplicated_result=duplicate_columns.empty
    if not duplicated_result:
        logging.info(f'Duplicated columns found : {duplicate_columns}')
    return duplicated_result
    