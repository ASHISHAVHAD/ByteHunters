from textblob import TextBlob

def analyze_sentiment_and_bias(text):
    """
    Analyzes the raw text to determine emotional tone and subjectivity.
    Returns a dictionary with scores and labels.
    """
    if not text:
        return None
        
    blob = TextBlob(text)
    
    polarity = blob.sentiment.polarity
    
    tone_label = "Neutral"
    if polarity > 0.1: tone_label = "Positive/Optimistic"
    elif polarity < -0.1: tone_label = "Negative/Critical"
    
    subjectivity = blob.sentiment.subjectivity
    
    bias_label = "Objective (Neutral)"
    if subjectivity > 0.3 and subjectivity <= 0.6:
        bias_label = "Slightly Opinionated"
    elif subjectivity > 0.6:
        bias_label = "Highly Biased / Opinion"

    return {
        "polarity_score": round(polarity, 2),
        "subjectivity_score": round(subjectivity * 100, 1),
        "tone_label": tone_label,
        "bias_label": bias_label
    }