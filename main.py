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

SITES = {
    "pornhub": "https://www.pornhub.com/video/search?search={query}",
    "xhamster": "https://xhamster.com/search/{query}",
    "xvideos": "https://www.xvideos.com/?k={query}"
}

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Send me a search query, e.g., 'cats' or 'xhamster cats'.")

@app.on_message(filters.text & ~filters.command(["start"]))
async def search(client, message):
    text = message.text.split()
    site = "pornhub"  # Default site
    query = message.text
    
    # Check if site is specified
    if len(text) > 1 and text[0].lower() in SITES:
        site = text[0].lower()
        query = " ".join(text[1:])
    
    await message.reply_text(f"Searching {site} for: {query}...")
    
    try:
        search_url = SITES[site].format(query=query)
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Site-specific selectors (update these after inspecting each site)
        selectors = {
            "pornhub": "li.pcVideoListItem div.phimage a",
            "xhamster": "div.video a.video-thumb__image-container",
            "xvideos": "div.mozaique div.thumb a"
        }
        
        video_elements = soup.select(selectors[site])
        if not video_elements:
            await message.reply_text(f"No videos found on {site}.")
            return
        
        video_links = []
        for elem in video_elements[:5]:
            href = elem.get("href")
            if href:
                full_url = href if href.startswith("http") else f"https://{site}.com{href}"
                video_links.append(full_url)
        
        response_text = f"Found {len(video_links)} videos on {site}:\n\n"
        for i, link in enumerate(video_links, 1):
            response_text += f"{i}. {link}\n"
        
        await message.reply_text(response_text)
        
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

print("Bot is running...")
app.run()
