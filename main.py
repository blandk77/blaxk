import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import yt_dlp

API_ID = ""
API_HASH = ""
BOT_TOKEN = ""

app = Client("PornhubBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


YDL_OPTIONS = {
    'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'merge_output_format': 'mp4',
    'quiet': True,
}


@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_text("Hello! Send me a Pornhub video URL or use /search <query> to find videos.")

@app.on_message(filters.regex(r'https?://(www\.)?pornhub\.com/view_video\.php\?viewkey=.+'))
async def download_video(client: Client, message: Message):
    url = message.text
    await message.reply_text("Downloading video, please wait...")
    
    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            video_title = info.get('title', 'video')

        
        await message.reply_video(
            video=video_path,
            caption=f"Here’s your video: {video_title}",
            supports_streaming=True
        )
        
        
        os.remove(video_path)
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

@app.on_message(filters.command("search"))
async def search_videos(client: Client, message: Message):
    query = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not query:
        await message.reply_text("Please provide a search query, e.g., /search hot videos")
        return
    
    await message.reply_text(f"Searching for '{query}'...")
    
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            
            search_url = f"https://www.pornhub.com/video/search?search={query}"
            result = ydl.extract_info(search_url, download=False)
            videos = result.get('entries', [])[:3]
            
            if not videos:
                await message.reply_text("No results found.")
                return
            
            response = "Search Results:\n"
            for idx, video in enumerate(videos, 1):
                title = video.get('title', 'Unknown Title')
                url = video.get('webpage_url', '#')
                response += f"{idx}. {title} - {url}\n"
            
            await message.reply_text(response + "\nSend a URL from the list to download!")
    except Exception as e:
        await message.reply_text(f"Error during search: {str(e)}")

if __name__ == "__main__":
    os.makedirs("downloads", exist_ok=True)
    print("Bot is running...")
    app.run()
