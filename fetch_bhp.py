import yfinance as yf
import pandas as pd
import math

TICKER = "BHP.AX"

def safe_get(d, key, default=None):
    return d.get(key, default) if isinstance(d, dict) else default


def main():
    t = yf.Ticker(TICKER)

    # Basic info
    info = t.info or {}
    price = info.get("regularMarketPrice")
    if price is None:
        hist = t.history(period="5d")
        price = hist['Close'].iloc[-1] if not hist.empty else None

    market_cap = info.get("marketCap")
    dividend_yield = info.get("dividendYield")
    previous_close = info.get("previousClose")

    print(f"Ticker: {TICKER}")
    print(f"Price: {price}")
    print(f"Previous close: {previous_close}")
    print(f"Market cap: {market_cap}")
    print(f"Dividend yield: {dividend_yield}")
    print("\n--- Financial statements (latest columns) ---\n")

    # Financial statements (yfinance returns DataFrames with periods as columns)
    try:
        fin = t.financials
        bs = t.balance_sheet
        cf = t.cashflow
    except Exception as e:
        fin = pd.DataFrame()
        bs = pd.DataFrame()
        cf = pd.DataFrame()

    def latest_col(df):
        if df is None or df.empty:
            return None
        return df.iloc[:, 0]

    latest_fin = latest_col(fin)
    latest_bs = latest_col(bs)
    latest_cf = latest_col(cf)

    if latest_fin is not None:
        print("Income statement (latest year):")
        print(latest_fin.dropna().to_string())
    else:
        print("Income statement not available via yfinance")

    print("")
    if latest_bs is not None:
        print("Balance sheet (latest year):")
        print(latest_bs.dropna().to_string())
    else:
        print("Balance sheet not available via yfinance")

    print("")
    if latest_cf is not None:
        print("Cash flow (latest year):")
        print(latest_cf.dropna().to_string())
    else:
        print("Cash flow not available via yfinance")

    # Compute a few ratios if possible
    print("\n--- Key ratios (approx) ---\n")
    try:
        revenue = float(latest_fin.get('Total Revenue') if 'Total Revenue' in latest_fin.index else (latest_fin.get('Revenue') if 'Revenue' in latest_fin.index else math.nan))
    except Exception:
        revenue = math.nan

    try:
        net_income = float(latest_fin.get('Net Income') if 'Net Income' in latest_fin.index else (latest_fin.get('NetIncome') if 'NetIncome' in latest_fin.index else math.nan))
    except Exception:
        net_income = math.nan

    try:
        total_assets = float(latest_bs.get('Total Assets') if 'Total Assets' in latest_bs.index else math.nan)
    except Exception:
        total_assets = math.nan

    try:
        total_liab = float(latest_bs.get('Total Liab') if 'Total Liab' in latest_bs.index else (latest_bs.get('Total Liabilities') if 'Total Liabilities' in latest_bs.index else math.nan))
    except Exception:
        total_liab = math.nan

    try:
        total_equity = float(latest_bs.get("Total Stockholder Equity") if "Total Stockholder Equity" in latest_bs.index else (latest_bs.get('Total Equity') if 'Total Equity' in latest_bs.index else math.nan))
    except Exception:
        total_equity = math.nan

    try:
        operating_cash_flow = float(latest_cf.get('Total Cash From Operating Activities') if 'Total Cash From Operating Activities' in latest_cf.index else (latest_cf.get('Operating Cash Flow') if 'Operating Cash Flow' in latest_cf.index else math.nan))
    except Exception:
        operating_cash_flow = math.nan

    # Ratios
    if not math.isnan(revenue) and not math.isnan(net_income):
        net_margin = net_income / revenue
        print(f"Net margin: {net_margin:.2%}")
    else:
        print("Net margin: N/A")

    if not math.isnan(total_equity) and not math.isnan(net_income) and total_equity != 0:
        roe = net_income / total_equity
        print(f"ROE: {roe:.2%}")
    else:
        print("ROE: N/A")

    if not math.isnan(total_assets) and not math.isnan(total_liab) and total_liab != 0:
        debt_to_assets = total_liab / total_assets
        print(f"Debt / Assets: {debt_to_assets:.2%}")
    else:
        print("Debt / Assets: N/A")

    # Current ratio if data present
    try:
        current_assets = float(latest_bs.get('Total Current Assets') if 'Total Current Assets' in latest_bs.index else (latest_bs.get('Current Assets') if 'Current Assets' in latest_bs.index else math.nan))
        current_liab = float(latest_bs.get('Total Current Liabilities') if 'Total Current Liabilities' in latest_bs.index else (latest_bs.get('Current Liabilities') if 'Current Liabilities' in latest_bs.index else math.nan))
        if not math.isnan(current_assets) and not math.isnan(current_liab) and current_liab != 0:
            current_ratio = current_assets / current_liab
            print(f"Current ratio: {current_ratio:.2f}")
        else:
            print("Current ratio: N/A")
    except Exception:
        print("Current ratio: N/A")

    # Dividend yield: yfinance provides as fraction
    if dividend_yield is not None:
        print(f"Dividend yield (info): {dividend_yield:.2%}")
    else:
        # fallback: compute from trailing annual dividend and price
        try:
            divs = t.dividends
            if not divs.empty:
                # trailing 12 months dividend
                recent = divs[-12:]
                # sum last 4 quarters / 12 months depending on frequency
                trailing = recent.groupby([recent.index.year, recent.index.quarter]).sum().sum()
                trailing = recent.sum()
                if price:
                    print(f"Dividend yield (trailing): {trailing/price:.2%}")
                else:
                    print("Dividend yield: N/A (no price)")
            else:
                print("Dividend yield: N/A (no dividends history)")
        except Exception:
            print("Dividend yield: N/A")

    # Print a tiny summary
    print("\n--- Quick summary ---")
    print(f"Price: {price} | Market cap: {market_cap} | Dividend yield (info): {dividend_yield}")


if __name__ == '__main__':
    main()
