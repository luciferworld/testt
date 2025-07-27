import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKUP_CHANNEL_ID = os.getenv("BACKUP_CHANNEL_ID")  # Format: -100XXXXXXXXXX
WORKER_URL = os.getenv("WORKER_URL")  # Your Worker URL

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    file = msg.document or msg.video or msg.audio or (msg.photo[-1] if msg.photo else None)

    if not file:
        await msg.reply_text("❗ Please send a document, video, audio or photo.")
        return

    fwd = await msg.forward(chat_id=BACKUP_CHANNEL_ID)
    f = fwd.document or fwd.video or fwd.audio or (fwd.photo[-1] if fwd.photo else None)
    
    if not f:
        await msg.reply_text("❌ Could not extract file ID.")
        return

    file_id = f.file_id
    link = f"{WORKER_URL}/?id={file_id}"

    await msg.reply_text(f"✅ File saved.\n🔗 [Download File]({link})", parse_mode="Markdown")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_file))
    print("Bot started...")
    app.run_polling()
