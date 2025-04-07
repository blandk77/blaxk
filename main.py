from pyrogram import Client, filters
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, Message
import yt_dlp
import asyncio

# Telegram bot credentials
api_id = "23340285"  # Replace with your api_id
api_hash = "ab18f905cb5f4a75d41bb48d20acfa50"  # Replace with your api_hash
bot_token = "7637037140:AAEItU6ezqzaxWKNBqintwmgBHHWktXwTOA"  # Replace with your bot token

# Initialize the Pyrogram client
app = Client("ph_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Hello! Send me a search query, and I'll try to find a video for you.")

# Handler for search queries
@app.on_message(filters.text & ~filters.command(["start"]))
async def search(client, message):
    query = message.text
    await message.reply_text(f"Searching for: {query}...")
    
    try:
        # Use yt-dlp to fetch video info (example for Pornhub)
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Replace with actual search logic or URL
            url = f"https://www.pornhub.com/video/search?search={query}"
            info = ydl.extract_info(url, download=False)  # Get metadata without downloading
            video_url = info['entries'][0]['url']  # First result
            
            # Optionally download the video
            ydl.download([video_url])
            
            # Send the video file (if under Telegram's file size limit, ~2GB for bots)
            await message.reply_video(video_url, caption=f"Found: {query}")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

# Run the bot
print("Bot is running...")
app.run()
