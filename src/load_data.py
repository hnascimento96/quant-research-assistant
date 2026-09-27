import yfinance as yf
import pandas as pd
from pathlib import Path
from src.config import DATE_END, DATE_START

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

TICKERS = {
    "^BVSP":  "IBOV",
    "^GSPC":  "SP500",
    "ITUB4.SA": "Itau",
    "VALE3.SA": "Vale",
    "PETR4.SA": "Petrobras",
}

def download(start=DATE_START, end=DATE_END):
    for ticker, name in TICKERS.items():
        df = yf.download(ticker, start=start, end=end, auto_adjust=True)
        df.to_csv(RAW_DIR / f"{name}.csv")
        print(f"{name}:{len(df)} downloaded lines")

if __name__ == "__main__":
    download()