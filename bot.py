import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv("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")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message"""
    await update.message.reply_text("Hello! I'm your AI assistant. Just send me a message and I'll respond.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    try:
        # Get response from OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": update.message.text}]
        )
        ai_response = response.choices[0].message.content
        await update.message.reply_text(ai_response)
    except Exception as e:
        await update.message.reply_text("Sorry, I encountered an error. Please try again.")

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(os.getenv("8008450858:AAGHGLf_BBL2uaoFjwXmhkREMikkS76tXkw")).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
