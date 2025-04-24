import os
import subprocess
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Bot configuration
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CRUNCHYROLL_EMAIL = os.getenv("CRUNCHYROLL_EMAIL")
CRUNCHYROLL_PASSWORD = os.getenv("CRUNCHYROLL_PASSWORD")
MULTI_DOWNLOADER_PATH = "/app/multi-downloader-nx"

# Initialize Pyrogram client
app = Client("crunchyroll_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Log startup
logger.info("Starting bot...")

# Start command
@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    logger.info(f"Received /start from {message.from_user.id}")
    await message.reply_text(
        "Welcome to the Crunchyroll Downloader Bot! 🦋\n"
        "Send /rip --srz <series_id> -e <episode> -q <quality> --dubLang <lang> --dlsubs <lang>\n"
        "Example: /rip --srz G4PH0WEKE -e 07 -q 5 --dubLang hin --dlsubs en\n"
        "Series ID: Extract from Crunchyroll series URL (e.g., https://www.crunchyroll.com/series/G4PH0WEKE/blue-lock)"
    )

# Rip command
@app.on_message(filters.command("rip"))
async def rip(client: Client, message: Message):
    try:
        logger.info(f"Received /rip from {message.from_user.id}")
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text(
                "Usage: /rip --srz <series_id> -e <episode> -q <quality> --dubLang <lang> --dlsubs <lang>\n"
                "Example: /rip --srz G4PH0WEKE -e 07 -q 5 --dubLang hin --dlsubs en"
            )
            return

        # Parse arguments
        series_id = None
        episode = "1"
        quality = "3"  # Default to max quality
        dub_lang = ["jpn"]  # Default to Japanese
        dl_subs = ["en"]  # Default to English subtitles

        i = 1
        while i < len(args):
            if args[i] == "--srz":
                series_id = args[i + 1]
                i += 2
            elif args[i] == "-e":
                episode = args[i + 1]
                i += 2
            elif args[i] == "-q":
                quality = args[i + 1]
                i += 2
            elif args[i] == "--dubLang":
                dub_lang = args[i + 1].split()
                i += 2
            elif args[i] == "--dlsubs":
                dl_subs = args[i + 1].split()
                i += 2
            else:
                i += 1

        if not series_id or not episode:
            await message.reply_text("Missing required arguments: --srz and -e are mandatory.")
            return

        await message.reply_text(f"Processing series {series_id}, episode {episode}...")
        logger.info(f"Processing series: {series_id}, episode: {episode}")

        output_file = "crunchyroll_video.mkv"
        cmd = [
            "node", f"{MULTI_DOWNLOADER_PATH}/lib/index.js",
            "--username", CRUNCHYROLL_EMAIL,
            "--password", CRUNCHYROLL_PASSWORD,
            "--output", output_file,
            "--srz", series_id,
            "-e", episode,
            "-q", quality,
            "--dubLang", *dub_lang,
            "--dlsubs", *dl_subs,
            "--merge-output-format", "mkv",
            "--crapi", "web",
            "--removeBumpers",
            "--chapters",
        ]
        await message.reply_text("Downloading video...")
        logger.info(f"Running command: {' '.join(cmd)}")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        last_progress = ""
        while process.poll() is None:
            line = process.stdout.readline().strip()
            if line and ("%" in line or "Downloading" in line or "Processing" in line):
                truncated_line = line[:4000]
                if truncated_line != last_progress:
                    try:
                        await message.reply_text(f"Progress: {truncated_line}")
                        logger.info(f"Download progress: {truncated_line}")
                        last_progress = truncated_line
                    except Exception as e:
                        logger.warning(f"Failed to send progress: {str(e)}")
        
        error_output = process.stdout.read() or "Unknown error"
        if process.returncode != 0:
            await message.reply_text(f"Download failed: {error_output[:4000]}")
            logger.error(f"Download failed: {error_output}")
            return

        if not os.path.exists(output_file):
            await message.reply_text("Error: Video file not found.")
            logger.error("Video file not found")
            return

        file_size = os.path.getsize(output_file)
        if file_size > 2 * 1024 * 1024 * 1024:
            await message.reply_text("Video too large, compressing...")
            logger.info("Compressing video due to size limit")
            compressed_file = "compressed_video.mkv"
            subprocess.run([
                "ffmpeg", "-i", output_file, "-c:v", "libx264", "-crf", "23",
                "-preset", "fast", "-c:a", "aac", "-b:a", "128k", compressed_file
            ])
            if os.path.exists(compressed_file):
                output_file = compressed_file
            else:
                await message.reply_text("Compression failed.")
                logger.error("Compression failed")
                return

        await message.reply_text("Uploading to Telegram...")
        logger.info("Uploading video to Telegram")
        await client.send_video(
            chat_id=message.chat.id,
            video=output_file,
            caption="Your Crunchyroll video! 🎥",
            supports_streaming=True
        )

        os.remove(output_file)
        if 'compressed_file' in locals() and os.path.exists(compressed_file):
            os.remove(compressed_file)
        await message.reply_text("Done! Video sent. 🥳")
        logger.info("Video sent successfully")

    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")
        logger.error(f"Error: {str(e)}")

# Run the bot
if __name__ == "__main__":
    logger.info("Bot running...")
    app.run()
