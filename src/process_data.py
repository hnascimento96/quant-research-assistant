import pandas as pd
import numpy as np
from pathlib import Path
from src.config import TICKERS, ROLLING_WINDOW_SIZE, B3_SECTOR_INDEXES

PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

RAW_DIR = Path("data/raw")

def get_basic_metrics(df, name):

    #daily returns
    df["Daily return"] = df['Close'].pct_change()
    df["Daily log-return"] = np.log(df['Close'] / df['Close'].shift(1))
    total_return = df["Daily log-return"].sum()

    
    #monthly returns
    monthly_prices = df['Close'].resample('ME').last()
    monthly_returns = pd.DataFrame(index=monthly_prices.index, 
                                   columns=["Monthly returns", "Monthly log-returns"])
    monthly_returns["Monthly returns"] = monthly_prices.pct_change()
    monthly_returns["Monthly log-returns"] = np.log(monthly_prices / monthly_prices.shift(1))
    mean_monthly_return_arith = monthly_returns["Monthly returns"].mean()
    mean_monthly_return_log = monthly_returns["Monthly log-returns"].mean()

    #volatility
    df[f"Volatility_{ROLLING_WINDOW_SIZE}"] = df['Daily log-return'].rolling(ROLLING_WINDOW_SIZE).std()*np.sqrt(252)
    volatility_mean = df[f"Volatility_{ROLLING_WINDOW_SIZE}"].mean()

    #drawdown
    peak = df["Close"].cummax()
    df["Drawdown"] = (df["Close"] - peak)/peak
    max_drawdown = df["Drawdown"].min()

    df.to_csv(PROCESSED_DIR / f"{name}_daily.csv")
    monthly_returns.to_csv(PROCESSED_DIR / f"{name}_monthly.csv")

    return max_drawdown, volatility_mean, total_return, mean_monthly_return_arith, mean_monthly_return_log

def process_data():

    summary_df = pd.DataFrame(columns=["asset", "max_drawdown", "volatility_mean",
                                    "total_return", "mean_monthly_return_arith", "mean_monthly_return_log"])

    for ticker in TICKERS:
        df = pd.read_csv(RAW_DIR / f"{ticker}.csv", index_col=0, parse_dates=True, skiprows=[1,2], dtype={
            "Close": float,
            "High": float,
            "Low": float,
            "Open": float,
            "Volume": float
        })

        df.index.name = "Date"

        max_drawdown, volatility_mean, total_return, mean_monthly_return_arith, mean_monthly_return_log = get_basic_metrics(df, ticker)
        summary_df.loc[len(summary_df)] = [ticker, max_drawdown, volatility_mean,
                                        total_return, mean_monthly_return_arith, mean_monthly_return_log]

    summary_df.to_csv(PROCESSED_DIR / f"summary.csv", index=False)
    print("Summary")
    print(summary_df)

def get_sector_indexes():
    months = {
        "Jan": 1,
        "Fev": 2,
        "Mar": 3,
        "Abr": 4,
        "Mai": 5,
        "Jun": 6,
        "Jul": 7,
        "Ago": 8,
        "Set": 9,
        "Out": 10,
        "Nov": 11,
        "Dez": 12
    }

    dfs = []

    for index in B3_SECTOR_INDEXES:
        df = pd.read_csv(
                RAW_DIR / f"{index.lower()}_daily_2026.csv",
                sep=";",
                encoding="latin1",
                skiprows=1
        )
        
        df = df[~df["Dia"].isin(["MÍNIMO", "MÁXIMO"])]

        df = df.melt(
            id_vars="Dia",
            var_name="Mes",
            value_name=index
        )

        df[index] = pd.to_numeric(
            df[index]
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False),
            errors="coerce"
        )

        df["Mes"] = df["Mes"].map(months)

        df["Date"] = pd.to_datetime(
            {
                "year": 2026,
                "month": df["Mes"],
                "day": df["Dia"]
            },
            errors="coerce"
        )

        df = df.set_index("Date")[[index]]
        df.dropna(inplace=True)

        dfs.append(df)

    return pd.concat(dfs, axis=1)

def returns_indexes():

    daily_return = get_sector_indexes()
    for index in daily_return.columns:
        daily_return[f"{index} (log) return"] = np.log(daily_return[index] / 
                                                           daily_return[index].shift(1))

    daily_return.to_csv(PROCESSED_DIR / "sector_indexes_daily.csv")

def process_sector_indexes():
    returns_indexes()

if __name__ == "__main__":
    process_sector_indexes()
    process_data()
    