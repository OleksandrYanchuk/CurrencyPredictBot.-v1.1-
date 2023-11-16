import asyncio
import glob
import json
import os
from datetime import datetime

import pandas as pd
from predict_bot import send_messages


def analysis_function(end_day_data, predicted_prices):
    # Округліть кожен елемент списку передбачених цін
    predicted_prices = [round(price, 6) for price in predicted_prices]

    actual_change = [
        (round((actual * 100), 6) / round(open_price, 6)) - 100
        for actual, open_price in zip(
            end_day_data["Close"], end_day_data["Open"]
        )
    ]
    predict_change = [
        (round((predicted * 100), 6) / round(open_price, 6)) - 100
        for predicted, open_price in zip(predicted_prices, end_day_data["Open"])
    ]

    actual_change = [round(change, 2) for change in actual_change]
    predict_change = [round(change, 2) for change in predict_change]

    actual_close_position = ""
    predict_close_position = ""

    for change in actual_change:
        if change > 0:
            actual_close_position += "bullish"
        elif change < 0:
            actual_close_position += "bearish"
        else:
            actual_close_position += "no changes"

    for change in predict_change:
        if change > 0:
            predict_close_position += "bullish"
        elif change < 0:
            predict_close_position += "bearish"
        else:
            predict_close_position += "no changes"

    direction = predict_close_position == actual_close_position

    return (
        f"Actual Change: {actual_change[0]} % {actual_close_position}\n"
        f"Predicted Change: {predict_change[0]} % {predict_close_position}\n"        
        f"Direction: {direction}"
    )


# Отримайте список файлів з фактичними цінами закриття та передбаченнями
end_day_data_files = glob.glob("currency_data/end_day_data_currency_*.csv")
prediction_files = glob.glob("currency_data/currency_predictions_*.json")

# Отримайте список унікальних дат з назв файлів
dates_end_day_data = [
    file.split("_")[-1].split(".")[0] for file in end_day_data_files
]
dates_predictions = [file.split("_")[-1].split(".")[0] for file in prediction_files]

# Знайдіть спільні дати для аналізу
common_dates = set(dates_end_day_data) & set(dates_predictions)


async def send_tg_message(end_day_data, common_dates):
    results = {}
    message = f"Результати аналізу передбачень за {datetime.today().date()}:\n"

    for date in common_dates:
        prediction_file = f"currency_data/currency_predictions_{date}.json"
        # Завантажте фактичні ціни закриття
        end_day_data = pd.read_csv(end_day_data)

        # Заванажте передбачення
        with open(prediction_file, "r") as json_file:
            predictions = json.load(json_file)

        # Виконайте аналіз для кожної валютної пари окремо
        for currency_pair, predicted_prices in predictions.items():
            # Виберіть дані для обраної валютної пари
            currency_data = end_day_data[
                end_day_data["Currency"] == currency_pair
            ]

            # Виконайте аналіз для цієї валютної пари
            analysis_result = analysis_function(currency_data, predicted_prices)

            # Створіть рядковий ключ, що містить інформацію про дату та валютну пару
            result_key = f"{currency_pair}"

            # Збережіть результати для кожної валютної пари з використанням рядкового ключа
            results[result_key] = analysis_result

            # Update the message string with the current currency pair's analysis result
            message += f"\n{currency_pair}:\n{analysis_result}\n\n"

    # Send the message to Telegram
    await send_messages(message)


async def main():
    if os.path.exists(f"currency_data/end_day_data_currency_{datetime.today().date()}.csv"):
        end_day_data_file_path = f"currency_data/end_day_data_currency_{datetime.today().date()}.csv"
        await send_tg_message(end_day_data_file_path, common_dates)

if __name__ == "__main__":
    asyncio.run(main())
