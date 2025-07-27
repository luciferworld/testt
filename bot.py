import os
import logging
from dotenv import load_dotenv
from telegram import Update, Document, Video, Audio, PhotoSize
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Load .env
load_dotenv()

# Read environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKUP_CHANNEL_ID = int(os.getenv("BACKUP_CHANNEL_ID"))
WORKER_URL = os.getenv("WORKER_URL")

# Logging (Optional but recommended)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Handler function
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    # Accept document, video, audio, or photo
    media = msg.document or msg.video or msg.audio or (msg.photo[-1] if msg.photo else None)
    if not media:
        await msg.reply_text("❗ Please send a document, video, audio, or photo.")
        return

    # Copy message to backup channel
    copied = await context.bot.copy_message(
        chat_id=BACKUP_CHANNEL_ID,
        from_chat_id=msg.chat_id,
        message_id=msg.message_id
    )

    # Extract file_id AFTER copy (copied msg retains same file_id)
    file_id = media.file_id
    filename = getattr(media, 'file_name', 'File')

    # Generate permanent download link using Cloudflare Worker
    link = f"{WORKER_URL}/?id={file_id}"
    await msg.reply_text(
        f"✅ File saved.\n📎 *{filename}*\n🔗 [Download File]({link})",
        parse_mode="Markdown"
    )

# Run bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_file))
    print("🤖 Bot started...")
    app.run_polling()

