from pyrogram import Client, filters
import requests
from bs4 import BeautifulSoup
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
    await message.reply_text("Hello! Send me a search query, and I'll find video links for you.")

# Handler for search queries
@app.on_message(filters.text & ~filters.command(["start"]))
async def search(client, message):
    query = message.text
    await message.reply_text(f"Searching for: {query}...")
    
    try:
        # Scrape Pornhub search results
        search_url = f"https://www.pornhub.com/video/search?search={query}"
        headers = {"User-Agent": "Mozilla/5.0"}  # Mimic a browser to avoid blocks
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find video links (adjust selector based on Pornhub's HTML structure)
        video_elements = soup.select("li.pcVideoListItem div.phimage a")
        if not video_elements:
            await message.reply_text("No videos found for your query.")
            return
        
        # Collect video URLs (limited to first 5 for brevity)
        video_links = []
        for elem in video_elements[:5]:
            video_path = elem.get("href")
            if video_path and "viewkey" in video_path:  # Ensure it's a video link
                full_url = f"https://www.pornhub.com{video_path}"
                video_links.append(full_url)
        
        if not video_links:
            await message.reply_text("No valid video links found.")
            return
        
        # Prepare response
        response_text = f"Found {len(video_links)} videos for '{query}':\n\n"
        for i, link in enumerate(video_links, 1):
            response_text += f"{i}. {link}\n"
        
        await message.reply_text(response_text)
        
        # Optionally fetch downloadable URLs with yt-dlp
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
        }
        for link in video_links:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
                downloadable_url = info.get('url', link)  # Fallback to original link if no URL
                await message.reply_text(f"Downloadable link: {downloadable_url}")
                
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

# Run the bot
print("Bot is running...")
app.run()
