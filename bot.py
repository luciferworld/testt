import os
import logging
import aiohttp
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKUP_CHANNEL_ID = int(os.getenv("BACKUP_CHANNEL_ID"))

logging.basicConfig(level=logging.INFO)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    media = msg.document or msg.video or msg.audio or (msg.photo[-1] if msg.photo else None)
    if not media:
        await msg.reply_text("❗ Please send a document, video, audio, or photo.")
        return

    # Step 1: Copy message to channel
    await context.bot.copy_message(
        chat_id=BACKUP_CHANNEL_ID,
        from_chat_id=msg.chat_id,
        message_id=msg.message_id
    )

    # Step 2: Get the file_id
    file_id = media.file_id
    filename = getattr(media, 'file_name', 'File')

    # Step 3: Use getFile to get file_path
    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
        async with session.get(url) as resp:
            data = await resp.json()

    if not data.get("ok"):
        await msg.reply_text("❌ Telegram CDN link could not be generated.")
        return

    file_path = data["result"]["file_path"]
    cdn_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    # Step 4: Reply with direct CDN URL
    await msg.reply_text(
        f"✅ File saved.\n📎 *{filename}*\n🔗 [Download File]({cdn_url})",
        parse_mode="Markdown"
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_file))
    print("🤖 Bot is running...")
    app.run_polling()
