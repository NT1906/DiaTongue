import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

API_URL = "http://localhost:8000/predict"  # Change later if deployed online
BOT_TOKEN = "8101564282:AAHfY3XWBDR_uVrn7jBd1cpAfGhlJuJURjc"

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a photo of your tongue 👅 for diabetes screening!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    img_data = requests.get(file.file_path).content

    files = {"file": img_data}
    response = requests.post(API_URL, files=files).json()

    prediction = response["prediction"]
    confidence = response["confidence"]

    await update.message.reply_text(
        f"Prediction: {prediction}\nConfidence: {confidence}"
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == '__main__':
    main()
