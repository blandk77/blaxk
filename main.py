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

# Command handler for /start
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_text("Hello! Send me a search query with /search <keyword> to find videos.")

@app.on_inline_query()
async def handle_inline_query(client: Client, inline_query: InlineQuery):
    query = inline_query.query.strip()
    if not query:
        await inline_query.answer(
            results=[],
            switch_pm_text="Type a search query",
            switch_pm_parameter="start"
        )
        return

    try:
        # Search Pornhub using yt-dlp
        ydl_opts = {"quiet": True, "default_search": "phsearch"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(query, download=False)
            videos = result.get("entries", [])[:10]  # Limit to 10 results

        if not videos:
            await inline_query.answer(
                results=[],
                switch_pm_text="No results found",
                switch_pm_parameter="start"
            )
            return

        # Build inline results
        results = []
        for index, video in enumerate(videos):
            title = video.get("title", "No title")
            url = video.get("webpage_url", "#")
            description = f"Duration: {video.get('duration', 'N/A')}s"

            # Use a unique ID based on query ID and index
            unique_id = f"{inline_query.id}_{index}"

            results.append(
                InlineQueryResultArticle(
                    id=unique_id,  # Unique ID for this query
                    title=title,
                    input_message_content=InputTextMessageContent(f"**{title}**\n{url}"),
                    description=description,
                    thumb_url=video.get("thumbnail", None)
                )
            )

        # Send the results
        await inline_query.answer(results=results, cache_time=1)

    except Exception as e:
        await inline_query.answer(
            results=[],
            switch_pm_text=f"Error: {str(e)}",
            switch_pm_parameter="start"
        )

# Run the bot
print("Inline bot is running...")
app.run()
