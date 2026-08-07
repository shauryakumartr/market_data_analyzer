"""Helper functions shared across analytics modules.
"""

import pandas as pd
import numpy as np

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero or NaN.
    """
    if pd.isna(numerator) or pd.isna(denominator):
        return default
    if denominator == 0.0:
        return default
    return float(numerator / denominator)

def calculate_ctr(clicks: float, impressions: float) -> float:
    """Calculate Click-Through Rate (CTR) in percentage.
    """
    return safe_divide(clicks, impressions) * 100.0

def calculate_cpc(spend: float, clicks: float) -> float:
    """Calculate Cost Per Click (CPC).
    """
    return safe_divide(spend, clicks)

def calculate_cpm(spend: float, impressions: float) -> float:
    """Calculate Cost Per Mille (CPM).
    """
    return safe_divide(spend, impressions) * 1000.0

def calculate_roas(revenue: float, spend: float) -> float:
    """Calculate Return on Ad Spend (ROAS).
    """
    return safe_divide(revenue, spend)

def calculate_conversion_rate(conversions: float, clicks: float) -> float:
    """Calculate Conversion Rate in percentage.
    """
    return safe_divide(conversions, clicks) * 100.0

def format_percentage(value: float) -> str:
    """Format numeric value as percentage string.
    """
    if pd.isna(value):
        return "0.00%"
    return f"{value:.2f}%"

def format_currency(value: float) -> str:
    """Format numeric value as Indian Rupees (INR) string.
    """
    if pd.isna(value):
        return "₹ 0.00"
    return f"₹ {value:,.2f}"

def top_n(df: pd.DataFrame, column: str, n: int = 5) -> pd.DataFrame:
    """Return top N rows sorted by column descending.
    """
    if df.empty or column not in df.columns:
        return df
    return df.sort_values(by=column, ascending=False).head(n)

def bottom_n(df: pd.DataFrame, column: str, n: int = 5) -> pd.DataFrame:
    """Return bottom N rows sorted by column ascending.
    """
    if df.empty or column not in df.columns:
        return df
    return df.sort_values(by=column, ascending=True).head(n)

def percentage_change(old_val: float, new_val: float) -> float:
    """Calculate percentage change from old_val to new_val.
    """
    if old_val == 0.0:
        return 0.0 if new_val == 0.0 else 100.0
    return ((new_val - old_val) / old_val) * 100.0

def add_performance_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize metrics and calculate a single weighted performance score (0-100).
    
    Weights:
    - ROAS: 35%
    - Conversion Rate: 25%
    - CTR: 15%
    - CPC (inverse): 15%
    - Spend Efficiency (conversions per INR): 10%
    """
    if df.empty:
        return df

    temp = df.copy()
    if 'ctr' not in temp.columns and 'Segment CTR' in temp.columns:
        temp['ctr'] = temp['Segment CTR']
    if 'conversion_rate' not in temp.columns and 'Segment Conversion Rate' in temp.columns:
        temp['conversion_rate'] = temp['Segment Conversion Rate']
    if 'cpc' not in temp.columns and 'Segment CPC' in temp.columns:
        temp['cpc'] = temp['Segment CPC']
    if 'spend_inr' not in temp.columns and 'Total Spend' in temp.columns:
        temp['spend_inr'] = temp['Total Spend']
    if 'conversions' not in temp.columns and 'Total Conversions' in temp.columns:
        temp['conversions'] = temp['Total Conversions']

    for col in ['roas', 'conversion_rate', 'ctr', 'cpc', 'spend_inr', 'conversions']:
        if col not in temp.columns:
            temp[col] = 0.0

    temp['spend_efficiency'] = temp.apply(lambda r: safe_divide(r['conversions'], r['spend_inr']), axis=1)

    def normalize(series: pd.Series, inverse: bool = False) -> pd.Series:
        s = pd.to_numeric(series, errors='coerce').fillna(0.0)
        s_min, s_max = s.min(), s.max()
        if s_max == s_min:
            return pd.Series(1.0, index=s.index)
        norm = (s - s_min) / (s_max - s_min)
        if inverse:
            norm = 1.0 - norm
        return norm

    norm_roas = normalize(temp['roas'])
    norm_cvr = normalize(temp['conversion_rate'])
    norm_ctr = normalize(temp['ctr'])
    norm_cpc = normalize(temp['cpc'], inverse=True)
    norm_eff = normalize(temp['spend_efficiency'])

    temp['performance_score'] = (
        norm_roas * 35.0 +
        norm_cvr * 25.0 +
        norm_ctr * 15.0 +
        norm_cpc * 15.0 +
        norm_eff * 10.0
    )

    def classify_tier(score: float) -> str:
        if score >= 85.0:
            return "Excellent"
        elif score >= 70.0:
            return "High Performer"
        elif score >= 50.0:
            return "Average"
        elif score >= 30.0:
            return "Underperforming"
        else:
            return "Critical"

    temp['performance_tier'] = temp['performance_score'].apply(classify_tier)
    
    df['performance_score'] = temp['performance_score']
    df['performance_tier'] = temp['performance_tier']
    return df

def classify_performance_majority(row: pd.Series, account_kpis: dict) -> str:
    """Classify an entity into High Performer, Low Performer, or Average Performer based on majority rule.
    """
    ctr = row.get('ctr', row.get('ctr_pct', 0.0))
    cvr = row.get('conversion_rate', row.get('conversion_rate_pct', 0.0))
    cpc = row.get('cpc', row.get('cpc_inr', 0.0))
    cpm = row.get('cpm', 0.0)
    cost_per_conv = row.get('cost_per_conversion', 0.0)
    roas = row.get('roas', 0.0)
    spend_share = row.get('spend_share', 0.0)
    conv_share = row.get('conversion_share', 0.0)

    avg_ctr = account_kpis.get('ctr', 0.0)
    avg_cvr = account_kpis.get('conversion_rate', 0.0)
    avg_cpc = account_kpis.get('cpc', 0.0)
    avg_cpm = account_kpis.get('cpm', 0.0)
    avg_cost_conv = safe_divide(account_kpis.get('spend', 0.0), account_kpis.get('conversions', 0.0))
    avg_roas = account_kpis.get('roas', 0.0)

    # Count high conditions
    high_conditions = [
        ctr > avg_ctr,
        cvr > avg_cvr,
        cpc < avg_cpc if cpc > 0 and avg_cpc > 0 else False,
        cpm < avg_cpm if cpm > 0 and avg_cpm > 0 else False,
        cost_per_conv < avg_cost_conv if cost_per_conv > 0 and avg_cost_conv > 0 else False,
        roas > avg_roas if roas > 0 and avg_roas > 0 else False,
        spend_share <= conv_share if (spend_share > 0 or conv_share > 0) else False
    ]

    low_conditions = [
        ctr < avg_ctr,
        cvr < avg_cvr,
        cpc > avg_cpc if cpc > 0 and avg_cpc > 0 else False,
        cpm > avg_cpm if cpm > 0 and avg_cpm > 0 else False,
        cost_per_conv > avg_cost_conv if cost_per_conv > 0 and avg_cost_conv > 0 else False,
        roas < avg_roas if roas > 0 and avg_roas > 0 else False,
        spend_share > conv_share if (spend_share > 0 or conv_share > 0) else False
    ]

    high_count = sum(high_conditions)
    low_count = sum(low_conditions)

    if high_count >= 4:
        return "High Performer"
    elif low_count >= 4:
        return "Low Performer"
    else:
        return "Average Performer"

def classify_budget_efficiency(spend_share: float, conv_share: float) -> str:
    """Classify budget efficiency: Efficient, Balanced, or Inefficient.
    """
    diff = conv_share - spend_share
    if diff > 2.0:
        return "Efficient"
    elif abs(diff) <= 2.0:
        return "Balanced"
    else:
        return "Inefficient"

def classify_opportunity(row: pd.Series, account_kpis: dict) -> str:
    """Classify opportunity tier: High Opportunity, Medium Opportunity, Low Opportunity.
    """
    ctr = row.get('ctr', 0.0)
    cvr = row.get('conversion_rate', 0.0)
    roas = row.get('roas', 0.0)
    spend_share = row.get('spend_share', 0.0)

    avg_ctr = account_kpis.get('ctr', 0.0)
    avg_cvr = account_kpis.get('conversion_rate', 0.0)
    avg_roas = account_kpis.get('roas', 0.0)

    # High Opportunity: High CTR, High CVR, High ROAS, Low Spend Share
    if ctr >= avg_ctr and cvr >= avg_cvr and (roas >= avg_roas or roas == 0) and spend_share < 25.0:
        return "High Opportunity"
    # Medium Opportunity: Good ROAS, Average Spend, Average CVR
    elif roas >= avg_roas * 0.8 or cvr >= avg_cvr * 0.8:
        return "Medium Opportunity"
    else:
        return "Low Opportunity"

def classify_risk(row: pd.Series, account_kpis: dict) -> str:
    """Classify risk tier: High Risk, Medium Risk, Low Risk.
    """
    ctr = row.get('ctr', 0.0)
    cvr = row.get('conversion_rate', 0.0)
    roas = row.get('roas', 0.0)
    spend_share = row.get('spend_share', 0.0)

    avg_ctr = account_kpis.get('ctr', 0.0)
    avg_cvr = account_kpis.get('conversion_rate', 0.0)
    avg_roas = account_kpis.get('roas', 0.0)

    negative_points = 0
    if ctr < avg_ctr: negative_points += 1
    if cvr < avg_cvr: negative_points += 1
    if roas < avg_roas and roas > 0: negative_points += 1
    if spend_share > 20.0: negative_points += 1

    if spend_share > 15.0 and negative_points >= 3:
        return "High Risk"
    elif spend_share > 10.0 and negative_points >= 2:
        return "Medium Risk"
    else:
        return "Low Risk"
