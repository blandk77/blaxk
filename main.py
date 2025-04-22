import os
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message

# Bot configuration
API_ID = "23340285"  # From https://my.telegram.org
API_HASH = "ab18f905cb5f4a75d41bb48d20acfa50"  # From https://my.telegram.org
BOT_TOKEN = "7092944338:AAEUyTpCAGoNJ4CbB9JC5Y6QSLBjC-wDtfY"  # From BotFather
CRUNCHYROLL_EMAIL = "helltv194@gmail.com"
CRUNCHYROLL_PASSWORD = "290104An."

# Initialize Pyrogram client
app = Client("crunchyroll_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Start command
@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text(
        "Welcome to the Crunchyroll Downloader Bot! 🦋\n"
        "Send /download <Crunchyroll episode URL> to download a video.\n"
        "Example: /download https://www.crunchyroll.com/watch/XXXXXX"
    )

# Download command
@app.on_message(filters.command("download"))
async def download(client: Client, message: Message):
    try:
        # Extract URL from command
        args = message.text.split(maxsplit=inux1)
        if len(args) < 2 or "crunchyroll.com" not in args[1]:
            await message.reply_text("Please provide a valid Crunchyroll episode URL:\n/download <URL>")
            return

        episode_url = args[1]
        await message.reply_text(f"Processing: {episode_url}...")

        # Define output file
        output_file = "downloaded_video.mp4"

        # Run crunchyroll-dl command
        cmd = [
            "crunchyroll-dl",
            "--email", CRUNCHYROLL_EMAIL,
            "--password", CRUNCHYROLL_PASSWORD,
            "-o", output_file,
            episode_url
        ]
        await message.reply_text("Downloading video...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Check if download was successful
        if result.returncode != 0:
            await message.reply_text(f"Download failed: {result.stderr}")
            return

        # Verify file exists
        if not os.path.exists(output_file):
            await message.reply_text("Error: Video file not found.")
            return

        # Send video to Telegram
        await message.reply_text("Uploading to Telegram...")
        await client.send_video(
            chat_id=message.chat.id,
            video=output_file,
            caption="Your Crunchyroll video! 🎥",
            supports_streaming=True
        )

        # Clean up
        os.remove(output_file)
        await message.reply_text("Done! Video sent. 🥳")

    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

# Run the bot
if __name__ == "__main__":
    app.run()

