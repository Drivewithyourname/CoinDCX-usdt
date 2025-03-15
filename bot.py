import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import asyncio
import nest_asyncio

# Apply nest_asyncio fix for Colab/Jupyter
nest_asyncio.apply()

# Your Telegram Bot Token
BOT_TOKEN = "7526934837:AAHqsEOl0NIwKtLX7BleUz9kywph-XqdvFA"

# Tax details
TRADING_FEE_PERCENT = 0.2  # Adjust based on exchange
BANK_TRANSFER_FEE_PERCENT = 0.1  # Adjust based on withdrawal method

# Store the previous price and the list of users who have started the bot
previous_price = None
users = set()

# Function to fetch real-time price from CoinDCX
async def get_usdt_to_inr():
    """Fetches real-time USDT to INR price from CoinDCX API."""
    url = "https://api.coindcx.com/exchange/ticker"
    response = requests.get(url)
    data = response.json()
    
    for ticker in data:
        if ticker['market'] == 'USDTINR':
            return float(ticker['last_price'])
    
    return None

# Function to handle price command
async def price(update: Update, context: CallbackContext):
    """Handles /price command to fetch and display USDT to INR conversion."""
    global previous_price
    usdt_to_inr = await get_usdt_to_inr()

    if usdt_to_inr:
        amount_before_tax = 1 * usdt_to_inr
        total_tax = amount_before_tax * ((TRADING_FEE_PERCENT + BANK_TRANSFER_FEE_PERCENT) / 100)
        amount_after_tax = amount_before_tax - total_tax

        message = (
            f"💰 **USDT to INR Price** 💰\n"
            f"1 USDT = {usdt_to_inr:.2f} INR\n\n"
            f"📌 **Before Tax:** {amount_before_tax:.2f} INR\n"
            f"⚡ **After Tax:** {amount_after_tax:.2f} INR"
        )

        # Check if the price has increased more than 90.5 INR
        if previous_price and usdt_to_inr - previous_price > 90.5:
            # Send a message to all users
            for user in users:
                await context.bot.send_message(chat_id=user, text="🚨 The price has increased by more than 90.5 INR! 🚨")

        # Update previous price
        previous_price = usdt_to_inr

    else:
        message = "⚠️ Unable to fetch USDT to INR price. Try again later."

    # Send the current price to the user who requested
    await update.message.reply_text(text=message, parse_mode="Markdown")

# Function to handle start command
async def start(update: Update, context: CallbackContext):
    """Handles /start command to register users."""
    users.add(update.message.chat_id)
    await update.message.reply_text("Hello! I will notify you about price changes.")

# Main function to start the bot
async def main():
    """Starts the bot."""
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("start", start))
    await app.run_polling()

# Run the bot with asyncio fix
asyncio.run(main())
