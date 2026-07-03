import logging
import pandas as pd 

def validation(df: pd.DataFrame) -> dict:

    """
         Validate the schema of the uploaded dataset.
         
         Checks:
         - Missing mandatory columns
         - Missing optional columns
         - Available derived columns
         
         Parameters
         ----------
         df : pandas.DataFrame
            Dataset uploaded by the user.
         
         Returns
         -------
         dict
            Dictionary containing the schema validation report.
         """
    #Column Validator
    logging.info('Checking for missing columns in dataframe')
    columns=set(df.columns)
    mandatory=set(['date','budget_inr','spend_inr','impressions','reach','clicks','conversions'])
    optional=set(['platform', 'campaign_name', 'ad_set_name', 'objective','result_type', 'region', 'age_group', 'gender', 'device','creative_format','add_to_cart', 'purchases'])
    derived=set(['ctr_pct', 'cpc_inr','conversion_rate_pct', 'cost_per_conversion_inr', 'roas'])
    columns_report=dict()
    
    #Checking for mandatory columns
    missing_mandatory=(mandatory)-(columns)
    if  missing_mandatory:
        columns_report['missing_mandatory']=missing_mandatory
        logging.warning(f'Missing mandatory columns found: {missing_mandatory}')

    #Checking for optional columns
    missing_optional=(optional)-(columns)
    if  missing_optional:
        columns_report['missing_optional']=missing_optional
        logging.warning(f"Missing optional columns found : {missing_optional}")

    #Checking for derived columns
    columns_report['derived_columns']=derived

    return columns_report


    
    