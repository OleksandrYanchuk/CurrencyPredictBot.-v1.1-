import asyncio
import json
import os

import aiohttp
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
import joblib
from sklearn.impute import SimpleImputer

from predict_bot import send_messages

today_date = datetime.today().date()


if f"currency_data/currency_predictions_{datetime.today().date()}.json":
    previous_predict = f"currency_data/currency_predictions_{datetime.today().date()}.json"

currency_data = pd.read_csv(
    f"currency_data/currency_data_with_all_indicators_{today_date}.csv",
    skiprows=[0],  # Пропустити перший рядок (назви стовпців)
    names=[
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Adj Close",
        "Volume",
        "Currency",
        "sentiment",
        "SMA_50",
        "SMA_200",
        "RSI",
        "MACD",
        "Signal_Line",
        "Bollinger_Band_Upper",
        "Bollinger_Band_Lower",
    ],
    dtype={
        "Open_Currency": float,
        "High_Currency": float,
        "Low_Currency": float,
        "Close_Currency": float,
        "Adj Close_Currency": float,
        "Volume_Currency": int,
        "sentiment": float,
    },
)

# Convert "Date" to datetime format
currency_data["Date"] = pd.to_datetime(currency_data["Date"])

# Create a copy of the DataFrame
today_data = currency_data[currency_data["Date"].dt.date == today_date].copy()

today_data["sentiment"] = today_data["sentiment"].fillna(0)

# Convert "Date" to timestamp
today_data["Date"] = today_data["Date"].apply(lambda x: x.timestamp())

label_encoder = LabelEncoder()
today_data["Currency_Currency_encoded"] = label_encoder.fit_transform(
    today_data["Currency"]
)

selected_columns = [
    "Date",
    "Open",
    "High",
    "Low",
    "Close",
    "Adj Close",
    "Currency_Currency_encoded",
    "sentiment",
    "SMA_50",
    "SMA_200",
    "RSI",
    "MACD",
    "Signal_Line",
    "Bollinger_Band_Upper",
    "Bollinger_Band_Lower",
]

current_directory = os.path.dirname(__file__)
file_path = "models/optimized_model.pkl"

model = joblib.load(file_path)

# Визначте унікальні валютні пари
unique_currency_pairs = today_data["Currency"].unique()

# Проведіть передбачення для кожної валютної пари
predictions_by_currency_pair = {}
for currency_pair in unique_currency_pairs:
    data_subset = today_data[today_data["Currency"] == currency_pair]
    X = data_subset[selected_columns]

    imputer = SimpleImputer(strategy="mean")

    # Fit and transform X
    X_imputed = imputer.fit_transform(X)

    # Predict without the feature_names argument
    predictions = model.predict(X_imputed)
    predictions_by_currency_pair[currency_pair] = predictions.tolist()

for currency_pair, predictions in predictions_by_currency_pair.items():
    # Remove the unnecessary .tolist() call
    predictions_by_currency_pair[currency_pair] = predictions


async def send_tg_message(previous_predictions, predictions_by_currency_pair):
    for currency_pair, current_predictions in predictions_by_currency_pair.items():
        if currency_pair in previous_predictions:
            previous_prices = previous_predictions[currency_pair]
            current_prices = current_predictions

            for previous_price, current_price in zip(previous_prices, current_prices):

                if previous_price != current_price:
                    await send_messages(f"Closing price for {currency_pair} has changed: Previous={previous_price}, Current={current_price}")

async def main():
    if os.path.exists(previous_predict):
        with open(previous_predict, "r") as json_file:
            previous_predictions = json.load(json_file)
            await send_tg_message(previous_predictions, predictions_by_currency_pair)

asyncio.run(main())




# Збережіть словник у JSON файл
file_name = f"currency_data/currency_predictions_{datetime.today().date()}.json"
with open(file_name, "w") as json_file:
    json.dump(predictions_by_currency_pair, json_file)
