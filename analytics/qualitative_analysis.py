"""Qualitative Ad Copy Analytics & Text Readability Engine.

Processes canonical marketing campaign data to extract copy length, word counts, formatting/visual rhythm metrics (emojis, line breaks, wall-of-text, mobile truncation),
promotional/urgency offer visibility, and textstat cognitive load readability scores.
"""

import re
import emoji
import pandas as pd
import textstat
import logging
from typing import Dict, Union, Optional

# Precompiled regex patterns for direct-response offer and urgency detection
OFFER_REGEX: re.Pattern = re.compile(
    r'(\d+%\s*off|[\$₹]\s*\d+\s*off|\bflat\b|\bdiscount\b|\bcode\b|\bcoupon\b|\bfree shipping\b|\bsale\b|\bbogo\b|\bdeal\b|\bsave\s*[\$₹]?)',
    re.IGNORECASE
)

URGENCY_REGEX: re.Pattern = re.compile(
    r'\b(today only|hurry|limited|ends soon|last chance|running out|don\'t wait)\b',
    re.IGNORECASE
)

# Module-level logger instance
logger: logging.Logger = logging.getLogger(__name__)


def _analyze_single_text(text: Optional[str], headline: Optional[str] = "") -> Dict[str, Union[int, float, bool]]:
    """Extract all text metrics and cognitive load scores in a single pass with micro-copy guardrails.

    Parameters
    ----------
    text : Optional[str]
        Raw primary ad copy text.
    headline : Optional[str], default=""
        Raw ad headline text.

    Returns
    -------
    Dict[str, Union[int, float, bool]]
        Extracted text metrics dictionary.
    """
    clean_text: str = "" if pd.isna(text) else str(text).strip()
    clean_headline: str = "" if pd.isna(headline) else str(headline).strip()
    
    char_len: int = len(clean_text)
    words: list[str] = re.findall(r'\w+', clean_text)
    word_count: int = len(words)
    
    # 1. Formatting & Visual Rhythm Metrics
    emojis: int = emoji.emoji_count(clean_text)
    emoji_density: float = round(emojis / max(word_count, 1), 4)
    line_breaks: int = len([l for l in clean_text.splitlines() if l.strip()])
    is_wall: bool = (char_len > 200) and (line_breaks <= 1)
    is_truncated: bool = char_len > 125
    
    # 2. Offer & Urgency Visibility
    offer_match = OFFER_REGEX.search(clean_text)
    has_offer: bool = bool(offer_match)
    has_offer_fold: bool = bool(has_offer and offer_match.start() <= 125)
    is_offer_buried: bool = has_offer and not has_offer_fold
    has_urgency: bool = bool(URGENCY_REGEX.search(clean_text))
    
    # 3. Readability Engine with Micro-Copy Guardrail (<10 words)
    if word_count < 10:
        reading_ease: float = 100.0
        grade_level: float = 1.0
        words_per_sentence: float = float(word_count)
        syllables_per_word: float = 1.0
        high_friction: bool = False
    else:
        try:
            # Replace newlines with periods to prevent bulleted lists being read as a single run-on sentence
            text_for_readability = clean_text.replace('\n', '. ')
            reading_ease = float(textstat.flesch_reading_ease(text_for_readability))
            grade_level = float(textstat.flesch_kincaid_grade(text_for_readability))
            s_count: int = max(textstat.sentence_count(text_for_readability), 1)
            words_per_sentence = round(word_count / s_count, 2)
            syllables: int = textstat.syllable_count(text_for_readability)
            syllables_per_word = round(syllables / max(word_count, 1), 2)
            high_friction = (grade_level > 9.0) or (words_per_sentence > 18.0)
        except Exception as exc:
            logger.error("Error computing textstat metrics for ad text snippet: %s", exc)
            reading_ease = 100.0
            grade_level = 1.0
            words_per_sentence = float(word_count)
            syllables_per_word = 1.0
            high_friction = False

    return {
        "text_length": char_len,
        "words_count": word_count,
        "headline_length": len(clean_headline),
        "emoji_count": emojis,
        "emoji_density": emoji_density,
        "line_breaks": line_breaks,
        "is_wall_of_text": is_wall,
        "is_mobile_truncated": is_truncated,
        "has_offer": has_offer,
        "has_offer_above_fold": has_offer_fold,
        "is_offer_buried": is_offer_buried,
        "has_urgency": has_urgency,
        "flesch_reading_ease": reading_ease,
        "flesch_kincaid_grade_level": grade_level,
        "average_words_per_sentence": words_per_sentence,
        "average_syllables_per_word": syllables_per_word,
        "is_high_cognitive_friction": high_friction,
    }


def text_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze ad copy text and return qualitative readability and format features.

    Parameters
    ----------
    df : pd.DataFrame
        Canonical marketing campaign DataFrame.

    Returns
    -------
    pd.DataFrame
        Qualitative feature DataFrame aligned with input metadata.
    """
    if not isinstance(df, pd.DataFrame):
        logger.error("Invalid input type provided to text_analysis: expected pd.DataFrame, received %s", type(df))
        return pd.DataFrame()

    if df.empty:
        logger.warning("Empty DataFrame passed to text_analysis. Skipping qualitative feature extraction.")
        return pd.DataFrame()

    if "primary_text" not in df.columns:
        logger.warning("'primary_text' column missing from DataFrame columns %s. Skipping text analysis.", list(df.columns))
        return pd.DataFrame()

    row_count: int = len(df)
    logger.info("Executing qualitative text analysis across %d records", row_count)

    try:
        # Extract features per row
        features: list[Dict[str, Union[int, float, bool]]] = [
            _analyze_single_text(row.get('primary_text', ''), row.get('headline', ''))
            for _, row in df.iterrows()
        ]
        
        feature_df: pd.DataFrame = pd.DataFrame(features)

        # Attach identifiers and base attributes
        id_col = df['ad_name'] if 'ad_name' in df.columns else df.get('campaign_name', 'Unknown')
        base_cols: pd.DataFrame = pd.DataFrame({
            'ad_name': id_col,
            'ad_set_name': df.get('ad_set_name', 'Unknown'),
            'text': df['primary_text'].fillna(''),
            'headline': df.get('headline', ''),
            'ad_description': df.get('ad_description', ''),
            'cta': df.get('cta', ''),
            'creative_format': df.get('creative_format', 'Unknown'),
            'creative_type': df.get('creative_type', 'Unknown'),
        })

        # Reset indexes to prevent row misalignment during horizontal concatenation
        base_cols = base_cols.reset_index(drop=True)
        feature_df = feature_df.reset_index(drop=True)

        qualitative_df: pd.DataFrame = pd.concat([base_cols, feature_df], axis=1)
        logger.info("Qualitative text analysis completed successfully. Output shape: (%d, %d)", len(qualitative_df), len(qualitative_df.columns))
        return qualitative_df

    except Exception as exc:
        logger.exception("Unexpected error encountered during qualitative text analysis: %s", exc)
        return pd.DataFrame()