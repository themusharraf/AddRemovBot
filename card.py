import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = 'your_api_token_here'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Connect to SQLite database
conn = sqlite3.connect('products.db')
cursor = conn.cursor()

# Create tables if not exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY,
        product_id INTEGER,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
''')
conn.commit()


# Product card layout
def generate_product_card(product_id, product_name, product_price):
    return f"🛒 Product ID: {product_id}\n🛍️ Name: {product_name}\n💵 Price: {product_price} USD"


# Handler for /start command
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Welcome! What would you like to do?", reply_markup=ReplyKeyboardRemove())


# Handler for /save_product command
@dp.message_handler(commands=['save_product'])
async def save_product(message: types.Message):
    # Simulating product details retrieval (replace with actual product retrieval logic)
    product_name = "Example Product"
    product_price = 10.99

    # Save product to database
    cursor.execute('INSERT INTO products (name, price) VALUES (?, ?)', (product_name, product_price))
    conn.commit()
    product_id = cursor.lastrowid

    # Generate product card
    product_card = generate_product_card(product_id, product_name, product_price)

    # Save product card to user's message
    await message.answer(product_card)


# Handler for /add_to_cart command
@dp.message_handler(commands=['add_to_cart'])
async def add_to_cart(message: types.Message):
    # Extract product ID from message
    try:
        product_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.answer("Invalid command usage. Use /add_to_cart <product_id>")
        return

    # Check if product exists
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    if product is None:
        await message.answer("Product not found.")
        return

    # Add product to cart
    cursor.execute('INSERT INTO cart (product_id) VALUES (?)', (product_id,))
    conn.commit()
    await message.answer(f"Product added to cart:\n{generate_product_card(product_id, product[1], product[2])}")


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(dp.skip_updates())
    executor = dp.loop.create_task(dp.start_polling())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(executor)
        loop.close()
