"""Helper functions shared across analytics modules.

Provides mathematical safe-division helpers, metric calculators (CTR, CPC, CPM, CVR, ROAS),
formatting utilities, scoring algorithms (0-100 weighted performance score), and majority rules classifiers.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union


def safe_divide(numerator: Union[float, int], denominator: Union[float, int], default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero or NaN.

    Parameters
    ----------
    numerator : Union[float, int]
        Dividend value.
    denominator : Union[float, int]
        Divisor value.
    default : float, default=0.0
        Fallback value if division is invalid.

    Returns
    -------
    float
        Quotient or default value.
    """
    if pd.isna(numerator) or pd.isna(denominator):
        return default
    if float(denominator) == 0.0:
        return default
    return float(numerator) / float(denominator)


def calculate_ctr(clicks: float, impressions: float) -> float:
    """Calculate Click-Through Rate (CTR) in percentage.

    Parameters
    ----------
    clicks : float
        Total clicks count.
    impressions : float
        Total impressions count.

    Returns
    -------
    float
        CTR percentage value (0.0 to 100.0).
    """
    return safe_divide(clicks, impressions) * 100.0


def calculate_cpc(spend: float, clicks: float) -> float:
    """Calculate Cost Per Click (CPC).

    Parameters
    ----------
    spend : float
        Total ad spend in INR.
    clicks : float
        Total clicks count.

    Returns
    -------
    float
        CPC value in INR.
    """
    return safe_divide(spend, clicks)


def calculate_cpm(spend: float, impressions: float) -> float:
    """Calculate Cost Per Mille (CPM) per thousand impressions.

    Parameters
    ----------
    spend : float
        Total ad spend in INR.
    impressions : float
        Total impressions count.

    Returns
    -------
    float
        CPM value in INR.
    """
    return safe_divide(spend, impressions) * 1000.0


def calculate_roas(revenue: float, spend: float) -> float:
    """Calculate Return on Ad Spend (ROAS).

    Parameters
    ----------
    revenue : float
        Total attributed revenue.
    spend : float
        Total ad spend in INR.

    Returns
    -------
    float
        ROAS multiplier ratio.
    """
    return safe_divide(revenue, spend)


def calculate_conversion_rate(conversions: float, clicks: float) -> float:
    """Calculate Conversion Rate in percentage.

    Parameters
    ----------
    conversions : float
        Total conversions count.
    clicks : float
        Total clicks count.

    Returns
    -------
    float
        Conversion rate percentage value (0.0 to 100.0).
    """
    return safe_divide(conversions, clicks) * 100.0


def format_percentage(value: float) -> str:
    """Format numeric value as a percentage string.

    Parameters
    ----------
    value : float
        Numeric percentage value.

    Returns
    -------
    str
        Formatted string (e.g. '5.20%').
    """
    if pd.isna(value):
        return "0.00%"
    return f"{float(value):.2f}%"


def format_currency(value: float) -> str:
    """Format numeric value as Indian Rupees (INR) string.

    Parameters
    ----------
    value : float
        Numeric currency amount.

    Returns
    -------
    str
        Formatted currency string (e.g. '₹ 1,500.50').
    """
    if pd.isna(value):
        return "₹ 0.00"
    return f"₹ {float(value):,.2f}"


def top_n(df: pd.DataFrame, column: str, n: int = 5) -> pd.DataFrame:
    """Return top N rows sorted by specified column descending.

    Parameters
    ----------
    df : pd.DataFrame
        Source DataFrame.
    column : str
        Sort column name.
    n : int, default=5
        Number of top records.

    Returns
    -------
    pd.DataFrame
        Top N DataFrame view.
    """
    if df.empty or column not in df.columns:
        return df
    return df.sort_values(by=column, ascending=False).head(n)


def bottom_n(df: pd.DataFrame, column: str, n: int = 5) -> pd.DataFrame:
    """Return bottom N rows sorted by specified column ascending.

    Parameters
    ----------
    df : pd.DataFrame
        Source DataFrame.
    column : str
        Sort column name.
    n : int, default=5
        Number of bottom records.

    Returns
    -------
    pd.DataFrame
        Bottom N DataFrame view.
    """
    if df.empty or column not in df.columns:
        return df
    return df.sort_values(by=column, ascending=True).head(n)


def percentage_change(old_val: float, new_val: float) -> float:
    """Calculate percentage change from old_val to new_val.

    Parameters
    ----------
    old_val : float
        Baseline value.
    new_val : float
        New comparison value.

    Returns
    -------
    float
        Percentage delta.
    """
    if float(old_val) == 0.0:
        return 0.0 if float(new_val) == 0.0 else 100.0
    return ((float(new_val) - float(old_val)) / float(old_val)) * 100.0


def add_performance_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize metrics and calculate a single weighted performance score (0-100).
    
    Weights:
    - ROAS: 35%
    - Conversion Rate: 25%
    - CTR: 15%
    - CPC (inverse): 15%
    - Spend Efficiency (conversions per INR): 10%

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame with performance_score and performance_tier columns added.
    """
    if df.empty:
        return df

    temp: pd.DataFrame = df.copy()
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
        s: pd.Series = pd.to_numeric(series, errors='coerce').fillna(0.0)
        s_min: float = float(s.min())
        s_max: float = float(s.max())
        if s_max == s_min:
            return pd.Series(1.0, index=s.index)
        norm: pd.Series = (s - s_min) / (s_max - s_min)
        if inverse:
            norm = 1.0 - norm
        return norm

    norm_roas: pd.Series = normalize(temp['roas'])
    norm_cvr: pd.Series = normalize(temp['conversion_rate'])
    norm_ctr: pd.Series = normalize(temp['ctr'])
    norm_cpc: pd.Series = normalize(temp['cpc'], inverse=True)
    norm_eff: pd.Series = normalize(temp['spend_efficiency'])

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


def classify_performance_majority(row: pd.Series, account_kpis: Dict[str, float]) -> str:
    """Classify an entity into High Performer, Low Performer, or Average Performer based on majority rules.

    Parameters
    ----------
    row : pd.Series
        Series containing entity metrics.
    account_kpis : Dict[str, float]
        Global account KPIs used as benchmarks.

    Returns
    -------
    str
        Performance classification category.
    """
    ctr: float = float(row.get('ctr', row.get('ctr_pct', 0.0)))
    cvr: float = float(row.get('conversion_rate', row.get('conversion_rate_pct', 0.0)))
    cpc: float = float(row.get('cpc', row.get('cpc_inr', 0.0)))
    cpm: float = float(row.get('cpm', 0.0))
    cost_per_conv: float = float(row.get('cost_per_conversion', 0.0))
    roas: float = float(row.get('roas', 0.0))
    spend_share: float = float(row.get('spend_share', 0.0))
    conv_share: float = float(row.get('conversion_share', 0.0))

    avg_ctr: float = account_kpis.get('ctr', 0.0)
    avg_cvr: float = account_kpis.get('conversion_rate', 0.0)
    avg_cpc: float = account_kpis.get('cpc', 0.0)
    avg_cpm: float = account_kpis.get('cpm', 0.0)
    avg_cost_conv: float = safe_divide(account_kpis.get('spend', 0.0), account_kpis.get('conversions', 0.0))
    avg_roas: float = account_kpis.get('roas', 0.0)

    # Count high conditions
    high_conditions: List[bool] = [
        ctr > avg_ctr,
        cvr > avg_cvr,
        cpc < avg_cpc if cpc > 0 and avg_cpc > 0 else False,
        cpm < avg_cpm if cpm > 0 and avg_cpm > 0 else False,
        cost_per_conv < avg_cost_conv if cost_per_conv > 0 and avg_cost_conv > 0 else False,
        roas > avg_roas if roas > 0 and avg_roas > 0 else False,
        spend_share <= conv_share if (spend_share > 0 or conv_share > 0) else False
    ]

    low_conditions: List[bool] = [
        ctr < avg_ctr,
        cvr < avg_cvr,
        cpc > avg_cpc if cpc > 0 and avg_cpc > 0 else False,
        cpm > avg_cpm if cpm > 0 and avg_cpm > 0 else False,
        cost_per_conv > avg_cost_conv if cost_per_conv > 0 and avg_cost_conv > 0 else False,
        roas < avg_roas if roas > 0 and avg_roas > 0 else False,
        spend_share > conv_share if (spend_share > 0 or conv_share > 0) else False
    ]

    high_count: int = sum(high_conditions)
    low_count: int = sum(low_conditions)

    if high_count >= 4:
        return "High Performer"
    elif low_count >= 4:
        return "Low Performer"
    else:
        return "Average Performer"


def classify_budget_efficiency(spend_share: float, conv_share: float) -> str:
    """Classify budget efficiency into Efficient, Balanced, or Inefficient.

    Parameters
    ----------
    spend_share : float
        Percentage of total spend.
    conv_share : float
        Percentage of total conversions.

    Returns
    -------
    str
        Budget efficiency status.
    """
    diff: float = conv_share - spend_share
    if diff > 2.0:
        return "Efficient"
    elif abs(diff) <= 2.0:
        return "Balanced"
    else:
        return "Inefficient"


def classify_opportunity(row: pd.Series, account_kpis: Dict[str, float]) -> str:
    """Classify opportunity tier: High Opportunity, Medium Opportunity, Low Opportunity.

    Parameters
    ----------
    row : pd.Series
        Entity metric series.
    account_kpis : Dict[str, float]
        Global account KPIs.

    Returns
    -------
    str
        Opportunity classification.
    """
    ctr: float = float(row.get('ctr', 0.0))
    cvr: float = float(row.get('conversion_rate', 0.0))
    roas: float = float(row.get('roas', 0.0))
    spend_share: float = float(row.get('spend_share', 0.0))

    avg_ctr: float = account_kpis.get('ctr', 0.0)
    avg_cvr: float = account_kpis.get('conversion_rate', 0.0)
    avg_roas: float = account_kpis.get('roas', 0.0)

    if ctr >= avg_ctr and cvr >= avg_cvr and (roas >= avg_roas or roas == 0) and spend_share < 25.0:
        return "High Opportunity"
    elif roas >= avg_roas * 0.8 or cvr >= avg_cvr * 0.8:
        return "Medium Opportunity"
    else:
        return "Low Opportunity"


def classify_risk(row: pd.Series, account_kpis: Dict[str, float]) -> str:
    """Classify risk tier: High Risk, Medium Risk, Low Risk.

    Parameters
    ----------
    row : pd.Series
        Entity metric series.
    account_kpis : Dict[str, float]
        Global account KPIs.

    Returns
    -------
    str
        Risk classification.
    """
    ctr: float = float(row.get('ctr', 0.0))
    cvr: float = float(row.get('conversion_rate', 0.0))
    roas: float = float(row.get('roas', 0.0))
    spend_share: float = float(row.get('spend_share', 0.0))

    avg_ctr: float = account_kpis.get('ctr', 0.0)
    avg_cvr: float = account_kpis.get('conversion_rate', 0.0)
    avg_roas: float = account_kpis.get('roas', 0.0)

    negative_points: int = 0
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
