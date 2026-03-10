import yfinance as yf
import json

TICKERS = ['BHP.AX','RIO.AX','FMG.AX']

rows = []
for tk in TICKERS:
    t = yf.Ticker(tk)
    info = t.info or {}
    market_cap = info.get('marketCap')
    current_price = info.get('currentPrice') or info.get('regularMarketPrice')
    currency = info.get('currency')
    trailingPE = info.get('trailingPE')
    forwardPE = info.get('forwardPE')
    enterpriseValue = info.get('enterpriseValue')
    ebitda = info.get('ebitda')
    revenue = info.get('totalRevenue') or info.get('revenue')
    ev_ebitda = None
    ev_revenue = None
    if enterpriseValue and ebitda:
        try:
            ev_ebitda = enterpriseValue / ebitda
        except Exception:
            ev_ebitda = None
    if enterpriseValue and revenue:
        try:
            ev_revenue = enterpriseValue / revenue
        except Exception:
            ev_revenue = None

    rows.append({
        'ticker': tk,
        'price': current_price,
        'currency': currency,
        'marketCap': market_cap,
        'trailingPE': trailingPE,
        'forwardPE': forwardPE,
        'enterpriseValue': enterpriseValue,
        'ebitda': ebitda,
        'revenue': revenue,
        'ev_ebitda': ev_ebitda,
        'ev_revenue': ev_revenue,
    })

print(json.dumps(rows, indent=2))
