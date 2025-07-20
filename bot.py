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

# Configure enhanced logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables securely
load_dotenv()

# Configuration with validation
try:
    CONFIG = {
        "TELEGRAM_TOKEN": os.environ["8008450858:AAGHGLf_BBL2uaoFjwXmhkREMikkS76tXkw"],
        "OPENAI_API_KEY": os.environ["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"],
        "ALLOWED_USER_IDS": (
            set(map(int, os.getenv("ALLOWED_USER_IDS", "").split(',')))
            if os.getenv("ALLOWED_USER_IDS")
            else None
        ),
        "ADMIN_USER_ID": (
            int(os.getenv("7697559889"))
            if os.getenv("ADMIN_USER_ID")
            else None
        ),
        "MODEL": os.getenv("MODEL", "gpt-3.5-turbo"),
        "MAX_TOKENS": int(os.getenv("MAX_TOKENS", 1000)),
        "TEMPERATURE": float(os.getenv("TEMPERATURE", 0.7))
    }
except KeyError as e:
    logger.error(f"Missing required environment variable: {e}")
    raise

# Initialize OpenAI with configuration
openai.api_key = CONFIG["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"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced welcome message with user awareness"""
    user = update.effective_user
    welcome_msg = f"""
    🎉 Welcome {user.mention_html()}! 🎉

    I'm your AI-powered Telegram assistant with:
    - Context-aware conversations
    - Multi-user support
    - Admin controls

    📝 Just send me a message to chat!
    ℹ️ Use /help for commands
    """
    await update.message.reply_html(welcome_msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dynamic help command showing available features"""
    help_text = """
    🤖 <b>AI Assistant Help</b> 🤖

    <u>Core Features</u>:
    - Natural language conversations
    - Context memory (/reset to clear)
    - Secure access control

    <u>Commands</u>:
    /start - Welcome message
    /help - This help menu  
    /reset - Clear conversation history
    /status - Show bot health (admin only)
    """
    await update.message.reply_html(help_text)

async def reset_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Secure context reset with confirmation"""
    if "messages" in context.chat_data:
        del context.chat_data["messages"]
        await update.message.reply_text("✅ Conversation history cleared!")
    else:
        await update.message.reply_text("No active conversation to reset.")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin-only status check"""
    if update.effective_user.id != CONFIG["ADMIN_USER_ID"]:
        await update.message.reply_text("⛔ Admin access required")
        return
    
    status_msg = f"""
    🖥️ <b>Bot Status</b> 🖥️
    
    <b>Model</b>: {CONFIG['MODEL']}
    <b>Tokens</b>: {CONFIG['MAX_TOKENS']}
    <b>Temp</b>: {CONFIG['TEMPERATURE']}
    <b>Users</b>: {'Restricted' if CONFIG['ALLOWED_USER_IDS'] else 'Open'}
    """
    await update.message.reply_html(status_msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Secure message handler with enhanced features"""
    # Access control
    if CONFIG["ALLOWED_USER_IDS"] and update.effective_user.id not in CONFIG["ALLOWED_USER_IDS"]:
        await update.message.reply_text("🔒 Unauthorized access")
        return

    # Initialize conversation history
    if "messages" not in context.chat_data:
        context.chat_data["messages"] = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
    
    # Add user message to history
    context.chat_data["messages"].append(
        {"role": "user", "content": update.message.text}
    )
    
    try:
        # Typing indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        # Get AI response
        response = await openai.ChatCompletion.acreate(
            model=CONFIG["MODEL"],
            messages=context.chat_data["messages"],
            temperature=CONFIG["TEMPERATURE"],
            max_tokens=CONFIG["MAX_TOKENS"]
        )
        
        ai_response = response.choices[0].message.content
        context.chat_data["messages"].append(
            {"role": "assistant", "content": ai_response}
        )
        
        await update.message.reply_text(ai_response)
        
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        error_msg = "⚠️ Service unavailable. Please try later."
        if CONFIG["ADMIN_USER_ID"]:
            await notify_admin(context, f"Error: {str(e)}")
        await update.message.reply_text(error_msg)

async def notify_admin(context: ContextTypes.DEFAULT_TYPE, message: str):
    """Secure admin notification handler"""
    try:
        await context.bot.send_message(
            chat_id=CONFIG["7697559889"],
            text=f"🚨 Bot Alert:\n\n{message}"
        )
    except Exception as e:
        logger.error(f"Admin notify failed: {str(e)}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced global error handler"""
    logger.error(f"Update {update} caused error: {context.error}")
    
    if CONFIG["ADMIN_USER_ID"]:
        await notify_admin(
            context,
            f"Error in update:\n\n{context.error}\n\nFrom: {update.effective_user.id}"
        )

def main():
    """Configure and start the bot"""
    app = Application.builder() \
        .token(CONFIG["8008450858:AAGHGLf_BBL2uaoFjwXmhkREMikkS76tXkw"]) \
        .defaults(Defaults(parse_mode="HTML")) \
        .post_init(post_init) \
        .build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("reset", reset_context))
    app.add_handler(CommandHandler("status", status_command))
    
    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    app.add_error_handler(error_handler)

    logger.info("Starting bot in polling mode...")
    app.run_polling(drop_pending_updates=True)

async def post_init(application: Application):
    """Post-initialization actions"""
    await application.bot.set_my_commands([
        ("start", "Start the bot"),
        ("help", "Show help"),
        ("reset", "Reset conversation"),
        ("status", "Bot status (admin)")
    ])

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}")
        raise
