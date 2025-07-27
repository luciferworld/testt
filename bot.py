import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKUP_CHANNEL_ID = int(os.getenv("BACKUP_CHANNEL_ID"))  # e.g., -1001234567890
WORKER_URL = os.getenv("WORKER_URL")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    file = msg.document or msg.video or msg.audio or (msg.photo[-1] if msg.photo else None)
    if not file:
        await msg.reply_text("❗ Please send a document, video, audio, or photo.")
        return

    # Copy message to backup channel (no forward tag, preserves file_id)
    copied = await context.bot.copy_message(
        chat_id=BACKUP_CHANNEL_ID,
        from_chat_id=msg.chat_id,
        message_id=msg.message_id
    )

    # Fetch copied message to get the new file_id
    copied_msg = await context.bot.get_chat_member(BACKUP_CHANNEL_ID, context.bot.id)  # ensures bot is in channel
    channel_msg = await context.bot.get_chat(BACKUP_CHANNEL_ID)
    copied_file_msg = await context.bot.get_message(BACKUP_CHANNEL_ID, copied.message_id)

    # Extract the file from copied message
    f = copied_file_msg.document or copied_file_msg.video or copied_file_msg.audio or (copied_file_msg.photo[-1] if copied_file_msg.photo else None)
    if not f:
        await msg.reply_text("❌ Could not extract file ID.")
        return

    file_id = f.file_id
    filename = getattr(f, 'file_name', 'File')

    # Build permanent link
    link = f"{WORKER_URL}/?id={file_id}"
    await msg.reply_text(f"✅ File saved to cloud.\n📎 *{filename}*\n🔗 [Download File]({link})", parse_mode="Markdown")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_file))
    print("Bot is running...")
    app.run_polling()
