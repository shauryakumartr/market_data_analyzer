import pandas as pd 

def filter_data(df, campaign_objective, device, gender, age_group, campaign_name):

    # Filter by Campaign Objective
    if campaign_objective != "All":
        filtered_df = df[df['objective'] == campaign_objective]
    else:
        filtered_df = df

    # Filter by Device
    if device:
        filtered_df = filtered_df[filtered_df['device'].isin(device)]

    # Filter by Gender
    if gender:
        filtered_df = filtered_df[filtered_df['gender'].isin(gender)]

    # Filter by Age Group
    if age_group:
        filtered_df = filtered_df[filtered_df['age_group'].isin(age_group)]

    # Filter by Campaign Name
    if campaign_name:
        filtered_df = filtered_df[filtered_df['campaign_name'].isin(campaign_name)]

    return filtered_df