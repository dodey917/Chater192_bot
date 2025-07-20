import os
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Bot settings
BOT_TOKEN = os.getenv('8008450858:AAGHGLf_BBL2uaoFjwXmhkREMikkS76tXkw')
BOT_USERNAME = "Chater192_bot"  # Replace with your bot's username

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! I\'m your AI-powered chatbot. Ask me anything!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    I'm an AI chatbot powered by OpenAI. Just send me a message and I'll respond!
    
    Commands:
    /start - Start the bot
    /help - Show this help message
    """
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            text = text.replace(BOT_USERNAME, '').strip()
        else:
            return

    # Get response from OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text}
            ]
        )
        ai_response = response.choices[0].message.content
    except Exception as e:
        ai_response = f"Sorry, I encountered an error: {str(e)}"

    await update.message.reply_text(ai_response)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error_handler)

    print('Polling...')
    app.run_polling(poll_interval=3)
