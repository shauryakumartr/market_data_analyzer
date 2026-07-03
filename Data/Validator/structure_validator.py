import pandas as pd 
import logging 
def structure_validation(df: pd.DataFrame) -> dict:
    logging.info('Checking for structural Validation of Dataframe')
    report=dict()

    #Dataframe Validator
    if df.empty:
        report['empty'] = True
        logging.warning('Dataframe is empty')  
    
    #Row Count Validator
    if len(df.index)<10:
        report['low_row_count']=True
        logging.warning("Dataframe has less than 10 rows")
    
    #Mandatory Columns Validator
    mandatory_columns=set(['date','budget_inr','spend_inr','impressions','reach','clicks','conversions'])
    for col in mandatory_columns:
        if df[col].empty:
            report['missing_mandatory_column']=col
            logging.warning(f'Mandatory column {col} is empty')
    
    #optional Columns Validator
    optional_columns=set(['platform', 'campaign_name', 'ad_set_name', 'objective','result_type', 'region', 'age_group', 'gender', 'device','creative_format','add_to_cart', 'purchases'])
    for col in optional_columns:
        if df[col].empty:
            report['missing_optional_column']=col
            logging.warning(f'Optional column {col} is empty')


    