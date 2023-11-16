import asyncio
import logging
import os
import json
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from currency_data.labels import currency

from dotenv import load_dotenv


load_dotenv()

json_file_path = "user_data.json"


# Функція для завантаження даних з JSON-файлу
def load_currency_data():
    file_name = f"currency_data/currency_predictions_{datetime.today().date()}.json"
    with open(file_name, "r") as json_file:
        data = json.load(json_file)
    return data


API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


items_per_page = 15

current_page = 1

currency_pairs = currency

currency_keyboard = InlineKeyboardMarkup()
for pair in currency_pairs:
    currency_keyboard.add(InlineKeyboardButton(text=pair, callback_data=f"pair_{pair}"))


# Function to read data from the JSON file
def read_json():
    try:
        with open(json_file_path, "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return []


# Function to write data to the JSON file
def write_json(data):
    with open(json_file_path, "w") as file:
        json.dump(data, file)


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id

    data = read_json()

    if {f"user_id_{user_id}": user_id} not in data:
        data.append({f"user_id_{user_id}": user_id})
        write_json(data)

    await show_currency_prediction(message, current_page)


@dp.callback_query_handler(lambda query: query.data == "prev_page_currency")
async def process_previous_page_currency(query: types.CallbackQuery):
    global current_page
    if current_page > 1:
        current_page -= 1
    await query.answer()
    await show_currency_prediction(query.message, current_page)


@dp.callback_query_handler(lambda query: query.data == "next_page_currency")
async def process_next_page_currency(query: types.CallbackQuery):
    global current_page
    current_page += 1
    await query.answer()
    await show_currency_prediction(query.message, current_page)


async def send_messages(message):
    user_ids = read_json()
    for user_dict in user_ids:  # Iterate through each dictionary
        for (
            user_id
        ) in user_dict.values():  # Iterate through all values in the dictionary
            try:
                await bot.send_message(user_id, message)
            except Exception as e:
                print(f"Failed to send message to user {user_id}: {e}")


async def show_currency_prediction(message, page):
    # Завантажте результати аналізу валютних пар
    currency_data = load_currency_data()

    # Створіть повідомлення з результатами аналізу для поточної сторінки
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    current_currency_pairs = list(currency_data.keys())[start_index:end_index]
    currency_data_message = f"Прогноз ціни закриття валютних пар на {datetime.today().date()}:\n"

    for currency_pair in current_currency_pairs:
        closing_price = currency_data[currency_pair]

        currency_data_message += f"\n{currency_pair}"
        currency_data_message += f" ціна закриття: {closing_price}\n"

    await message.answer(currency_data_message)

    # Побудуйте клавіатуру пагінації
    pagination_keyboard = InlineKeyboardMarkup()
    if page > 1:
        pagination_keyboard.add(
            InlineKeyboardButton(
                text="← Previous", callback_data="prev_page_currency"
            )
        )
    if end_index < len(currency_data):
        pagination_keyboard.add(
            InlineKeyboardButton(
                text="Next →", callback_data="next_page_currency"
            )
        )

    await message.answer("Пагінація:", reply_markup=pagination_keyboard)


if __name__ == "__main__":
    from aiogram import executor

    # Check if the script is being run directly
    if __name__ == "__main__":
        loop = asyncio.get_event_loop()
        # Start the background task to send messages
        executor.start_polling(dp, skip_updates=True)
