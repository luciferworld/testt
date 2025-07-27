import os
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

    # Extract supported media
    file = msg.document or msg.video or msg.audio or (msg.photo[-1] if msg.photo else None)
    if not file:
        await msg.reply_text("❗ Please send a document, video, audio, or photo.")
        return

    # Get file_id directly from user's message
    file_id = file.file_id
    filename = getattr(file, 'file_name', 'File')

    # Save it to your backup channel
    await context.bot.copy_message(
        chat_id=BACKUP_CHANNEL_ID,
        from_chat_id=msg.chat_id,
        message_id=msg.message_id
    )

    # Generate permanent link using your Cloudflare Worker
    link = f"{WORKER_URL}/?id={file_id}"

    await msg.reply_text(f"✅ File saved to cloud.\n📎 *{filename}*\n🔗 [Download File]({link})", parse_mode="Markdown")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_file))
    print("Bot is running...")
    app.run_polling()
