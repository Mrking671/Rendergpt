import os
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async

# Initialize Flask app
app = Flask(__name__)

# Telegram bot token
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = Bot(token=TOKEN)

# Dispatcher to register handlers
dispatcher = Dispatcher(bot, None, workers=0)

# API endpoint
API_URL = "https://telesevapi.vercel.app/gpt4"

def start(update, context):
    """Handler for the /start command."""
    update.message.reply_text("Hi there! Ask me anything, and I'll try to help.")

@run_async
def handle_message(update, context):
    """Handle incoming messages."""
    user_id = update.message.from_user.id
    question = update.message.text
    
    # Make a request to the API
    response = requests.get(API_URL, params={"id": user_id, "question": question})
    
    if response.status_code == 200:
        data = response.json()
        reply_message = data.get("message", "Sorry, I didn't understand that.")
        credit = data.get("Credit", "")
        update.message.reply_text(f"{reply_message}\n\nCredit: {credit}")
    else:
        update.message.reply_text("Sorry, something went wrong with the API request.")

# Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Set up a route for the webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

# Set webhook
@app.route("/set_webhook", methods=["GET", "POST"])
def set_webhook():
    s = bot.set_webhook(f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}")
    if s:
        return "Webhook set successfully"
    else:
        return "Webhook setup failed"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
