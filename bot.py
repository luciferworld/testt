import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKUP_CHANNEL_ID = int(os.getenv("BACKUP_CHANNEL_ID"))
WORKER_URL = os.getenv("WORKER_URL")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    file = msg.document or msg.video or msg.audio or (msg.photo[-1] if msg.photo else None)
    if not file:
        await msg.reply_text("❗ Please send a document, video, audio, or photo.")
        return

    # Copy to backup channel
    await context.bot.copy_message(
        chat_id=BACKUP_CHANNEL_ID,
        from_chat_id=msg.chat_id,
        message_id=msg.message_id
    )

    file_id = file.file_id
    filename = getattr(file, 'file_name', 'File')

    # Validate file_id via Telegram API to avoid "file not found"
    r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}")
    json = r.json()
    if not json.get("ok"):
        await msg.reply_text("❌ File not found or expired.")
        return

    # Generate download link via Cloudflare Worker
    link = f"{WORKER_URL}/?id={file_id}"
    await msg.reply_text(f"✅ File saved to cloud.\n📎 *{filename}*\n🔗 [Download File]({link})", parse_mode="Markdown")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_file))
    print("Bot is running...")
    app.run_polling()
