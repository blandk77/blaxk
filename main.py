from pyrogram import Client, filters
from pyrogram.types import Message
from pornhub_api import PornhubApi
import asyncio

# Telegram bot credentials
api_id = "YOUR_API_ID"  # Replace with your api_id
api_hash = "YOUR_API_HASH"  # Replace with your api_hash
bot_token = "YOUR_BOT_TOKEN"  # Replace with your bot token

# Initialize the Pyrogram client
app = Client("ph_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Pornhub API instance
ph_api = PornhubApi()

# Command handler for /start
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_text("Hello! Send me a search query with /search <keyword> to find videos.")

# Command handler for /search
@app.on_message(filters.command("search"))
async def search_videos(client: Client, message: Message):
    # Extract the search query from the message
    query = " ".join(message.command[1:])
    if not query:
        await message.reply_text("Please provide a search term, e.g., /search cats")
        return

    try:
        # Search Pornhub for the query
        search_results = ph_api.search.search(query)
        videos = search_results.videos

        if not videos:
            await message.reply_text("No videos found for that query.")
            return

        # Get the first video's details
        video = videos[0]
        title = video.title
        url = video.url

        # Reply with the video title and URL
        response = f"**Title**: {title}\n**URL**: {url}"
        await message.reply_text(response)

        # Optional: You could download the video here and send it instead
        # For now, we just send the URL due to file size limits

    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

# Run the bot
print("Bot is running...")
app.run()
