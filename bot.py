import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    Defaults
)
import openai
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
CONFIG = {
    "TELEGRAM_TOKEN": os.getenv("8008450858:AAGHGLf_BBL2uaoFjwXmhkREMikkS76tXkw"),
    "OPENAI_API_KEY": os.getenv("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"),
    "ALLOWED_USER_IDS": set(map(int, os.getenv("ALLOWED_USER_IDS", "").split(',')) if os.getenv("ALLOWED_USER_IDS") else None,
    "ADMIN_USER_ID": int(os.getenv("7697559889")) if os.getenv("ADMIN_USER_ID") else None
}

# Validate configuration
if not CONFIG["TELEGRAM_TOKEN"]:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
if not CONFIG["OPENAI_API_KEY"]:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize OpenAI
openai.api_key = CONFIG["OPENAI_API_KEY"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when the command /start is issued."""
    user = update.effective_user
    welcome_text = (
        f"Hello {user.mention_html()}! 👋\n\n"
        "I'm your AI-powered Telegram bot. You can ask me anything!\n\n"
        "Available commands:\n"
        "/start - Show this welcome message\n"
        "/help - Show help information\n"
        "/reset - Reset the conversation context"
    )
    await update.message.reply_html(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message when the command /help is issued."""
    help_text = (
        "🤖 <b>AI Assistant Bot Help</b>\n\n"
        "Just send me a message and I'll respond with AI-generated content!\n\n"
        "<b>Commands:</b>\n"
        "/start - Show welcome message\n"
        "/help - Show this help message\n"
        "/reset - Reset conversation history\n\n"
        "Note: I remember our conversation context within a single chat."
    )
    await update.message.reply_html(help_text)

async def reset_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset the conversation context."""
    if "messages" in context.chat_data:
        del context.chat_data["messages"]
    await update.message.reply_text("Conversation context has been reset.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages."""
    # Check if user is allowed (if ALLOWED_USER_IDS is set)
    if CONFIG["ALLOWED_USER_IDS"] and update.effective_user.id not in CONFIG["ALLOWED_USER_IDS"]:
        await update.message.reply_text("Sorry, you're not authorized to use this bot.")
        return

    user_message = update.message.text
    
    # Initialize or get conversation history
    if "messages" not in context.chat_data:
        context.chat_data["messages"] = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
    
    # Add user message to history
    context.chat_data["messages"].append({"role": "user", "content": user_message})
    
    try:
        # Get response from OpenAI
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=context.chat_data["messages"],
            temperature=0.7,
            max_tokens=1000
        )
        
        ai_response = response.choices[0].message.content
        # Add AI response to history
        context.chat_data["messages"].append({"role": "assistant", "content": ai_response})
        
        await update.message.reply_text(ai_response)
        
    except Exception as e:
        logger.error(f"Error in OpenAI API call: {e}")
        error_message = "Sorry, I encountered an error processing your request."
        if CONFIG["ADMIN_USER_ID"]:
            error_message += f"\n\nAdmin has been notified."
            try:
                await context.bot.send_message(
                    chat_id=CONFIG["ADMIN_USER_ID"],
                    text=f"Error in bot for user {update.effective_user.id}:\n\n{str(e)}"
                )
            except Exception as admin_error:
                logger.error(f"Failed to notify admin: {admin_error}")
        await update.message.reply_text(error_message)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors and send notification to admin if configured."""
    logger.error(f"Update {update} caused error {context.error}")
    
    if CONFIG["ADMIN_USER_ID"]:
        try:
            await context.bot.send_message(
                chat_id=CONFIG["ADMIN_USER_ID"],
                text=f"An error occurred:\n\n{context.error}"
            )
        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder() \
        .token(CONFIG["TELEGRAM_TOKEN"]) \
        .defaults(Defaults(parse_mode="HTML")) \
        .build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset_context))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)

    # Run the bot
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
