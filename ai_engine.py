def generate_ai_signal(pcr, support, resistance):

    if pcr > 1.2:
        sentiment = "Bullish 🚀"
        advice = "Buy on dips strategy can be considered."
    elif pcr < 0.8:
        sentiment = "Bearish 📉"
        advice = "Sell on rise strategy may work."
    else:
        sentiment = "Sideways ⚖️"
        advice = "Wait for breakout before entering trade."

    message = f"""
📊 Market Sentiment: {sentiment}

📉 Support Level: {support}
📈 Resistance Level: {resistance}

🧠 AI Insight:
{advice}
"""

    return message