import os
import logging
import aiohttp
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKUP_CHANNEL_ID = int(os.getenv("BACKUP_CHANNEL_ID"))
WORKER_URL = os.getenv("WORKER_URL")

logging.basicConfig(level=logging.INFO)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    media = msg.document or msg.video or msg.audio or (msg.photo[-1] if msg.photo else None)
    if not media:
        await msg.reply_text("❗ Please send a document, video, audio, or photo.")
        return

    # 1. Copy the message to your backup channel
    copied = await context.bot.copy_message(
        chat_id=BACKUP_CHANNEL_ID,
        from_chat_id=msg.chat_id,
        message_id=msg.message_id
    )

    copied_msg_id = copied.message_id

    # 2. Fetch copied message using Telegram Bot API HTTP (not python-telegram-bot)
    async with aiohttp.ClientSession() as session:
        api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        async with session.get(api_url) as res:
            data = await res.json()

    # 3. Try to find the copied message in updates
    file_id = None
    for result in reversed(data.get("result", [])):
        ch_msg = result.get("channel_post", {})
        if ch_msg.get("message_id") == copied_msg_id:
            media = ch_msg.get("document") or ch_msg.get("video") or ch_msg.get("audio") or None
            if not media and "photo" in ch_msg:
                media = ch_msg["photo"][-1]
            if media:
                file_id = media.get("file_id")
            break

    if not file_id:
        await msg.reply_text("❌ Failed to extract permanent file ID.")
        return

    filename = media.get("file_name", "File")

    # 4. Generate Cloudflare Worker link
    link = f"{WORKER_URL}/?id={file_id}"
    await msg.reply_text(
        f"✅ File saved.\n📎 *{filename}*\n🔗 [Download File]({link})",
        parse_mode="Markdown"
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_file))
    print("🤖 Bot running...")
    app.run_polling()
