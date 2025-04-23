import os
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CRUNCHYROLL_EMAIL = os.getenv("CRUNCHYROLL_EMAIL")
CRUNCHYROLL_PASSWORD = os.getenv("CRUNCHYROLL_PASSWORD")
MULTI_DOWNLOADER_PATH = "/app/multi-downloader-nx"  # Path in Koyeb container

# Initialize Pyrogram client
app = Client("crunchyroll_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Start command
@Client.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text(
        "Welcome to the Crunchyroll Downloader Bot! 🦋\n"
        "Send /download <Crunchyroll episode URL> to download a video.\n"
        "Example: /download https://www.crunchyroll.com/watch/G31UXQ3NP/izuku-midoriya-origin"
    )

# Download command
@Client.on_message(filters.command("download"))
async def download(client: Client, message: Message):
    try:
        # Extract URL from command
        args = message.text.split(maxsplit=1)
        if len(args) < 2 or "crunchyroll.com" not in args[1]:
            await message.reply_text("Please provide a valid Crunchyroll episode URL:\n/download <URL>")
            return

        episode_url = args[1]
        await message.reply_text(f"Processing: {episode_url}...")

        # Define output file
        output_file = "crunchyroll_video.mkv"

        # Run multi-downloader-nx command
        cmd = [
            "node", f"{MULTI_DOWNLOADER_PATH}/lib/index.js",
            "--username", CRUNCHYROLL_EMAIL,
            "--password", CRUNCHYROLL_PASSWORD,
            "--output", output_file,
            "--quality", "0",  # Maximum quality
            "--merge-output-format", "mkv",
            episode_url
        ]
        await message.reply_text("Downloading video...")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        while process.poll() is None:
            line = process.stdout.readline().strip()
            if line and ("%" in line or "Downloading" in line or "Processing" in line):
                await message.reply_text(f"Progress: {line}")

        # Check if download was successful
        if process.returncode != 0:
            error_output = process.stdout.read() or "Unknown error"
            await message.reply_text(f"Download failed: {error_output}")
            return

        # Verify file exists
        if not os.path.exists(output_file):
            await message.reply_text("Error: Video file not found.")
            return

        # Check file size (Telegram limit: 2GB)
        file_size = os.path.getsize(output_file)
        if file_size > 2 * 1024 * 1024 * 1024:
            await message.reply_text("Video too large, compressing...")
            compressed_file = "compressed_video.mkv"
            subprocess.run([
                "ffmpeg", "-i", output_file, "-c:v", "libx264", "-crf", "23",
                "-preset", "fast", "-c:a", "aac", "-b:a", "128k", compressed_file
            ])
            if os.path.exists(compressed_file):
                output_file = compressed_file
            else:
                await message.reply_text("Compression failed.")
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
        if 'compressed_file' in locals() and os.path.exists(compressed_file):
            os.remove(compressed_file)
        await message.reply_text("Done! Video sent. 🥳")

    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

# Run the bot
if __name__ == "__main__":
    app.run()
