import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

API_URL = "your_url"
BOT_TOKEN = "your_bot_token"

logging.basicConfig(level=logging.INFO)

WELCOME_MESSAGE = """
👋 Welcome to DiaTongue Bot!

I can help screen for diabetes by analyzing tongue images.

How to use:
1️⃣ Take a clear photo of your tongue
2️⃣ Send the photo to me
3️⃣ Wait for the analysis result

Commands:
/start - Show this welcome message
/help - Get help and tips

📸 Send a tongue photo to begin!
"""

HELP_MESSAGE = """
📖 DiaTongue Help

Tips for best results:
• Use good lighting
• Stick out your tongue fully
• Take a clear, focused photo
• Avoid filters or edits

Understanding results:
🟢 Non-Diabetic - No signs detected
🔴 Diabetic - Signs detected (consult a doctor)

⚠️ Disclaimer: This is a screening tool only. 
Always consult a healthcare professional for diagnosis.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_MESSAGE)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Send processing message
    processing_msg = await update.message.reply_text("🔬 Analyzing your tongue image...\n\nPlease wait a moment.")
    
    try:
        # Get the photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        img_data = requests.get(file.file_path).content

        # Send to API
        files = {"file": ("tongue.jpg", img_data, "image/jpeg")}
        response = requests.post(API_URL, files=files, timeout=30)
        
        if response.status_code != 200:
            await processing_msg.edit_text("❌ Error: Could not analyze image. Please try again later.")
            return
            
        data = response.json()
        prediction = data["prediction"]
        confidence = data["confidence"]
        confidence_percent = int(confidence * 100)
        
        # Format result
        if prediction == "Diabetic":
            result_text = f"""🔴 Result: {prediction}

📊 Confidence: {confidence_percent}%

⚠️ Important: This screening detected possible signs of diabetes. 
Please consult a healthcare professional for proper diagnosis.

This is not a medical diagnosis."""
        else:
            result_text = f"""🟢 Result: {prediction}

📊 Confidence: {confidence_percent}%

✅ No signs of diabetes detected in this screening.

This is not a medical diagnosis. Regular health checkups are recommended."""
        
        await processing_msg.edit_text(result_text)
        
    except requests.exceptions.Timeout:
        await processing_msg.edit_text("⏱️ Timeout: The server is taking too long. Please try again.")
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        await processing_msg.edit_text("❌ Error: Something went wrong. Please try again.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 Please send a photo of your tongue for analysis.\n\nType /help for tips on taking a good photo."
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    # Message handlers
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("🤖 DiaTongue Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
