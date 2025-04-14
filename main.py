from pyrogram import Client, filters, types
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent
from pornhub_api import Pornhub
import asyncio

# Bot configuration
API_ID = "your_api_id"  # From https://my.telegram.org
API_HASH = "your_api_hash"  # From https://my.telegram.org
BOT_TOKEN = "your_bot_token"  # From @BotFather

# Initialize Pyrogram client
app = Client("ph_search_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Initialize Pornhub API client
ph_client = Pornhub.Client()

# Handle inline queries
@app.on_inline_query()
async def handle_inline_query(client, inline_query):
    query = inline_query.query.strip()
    if not query:
        return  # Ignore empty queries

    try:
        # Search Pornhub videos (async)
        results = await ph_client.search(query, sort="mostviewed", page=1)
        inline_results = []

        # Limit to 10 results for demo
        for video in list(results)[:10]:
            inline_results.append(
                InlineQueryResultArticle(
                    id=video.id,  # Unique ID for the result
                    title=video.title,
                    description=f"Views: {video.views} | Duration: {video.duration}",
                    thumb_url=video.thumbnail or None,
                    input_message_content=InputTextMessageContent(
                        message_text=f"Video: {video.title}\nLink: {video.url}"
                    )
                )
            )

        # Send inline results
        await inline_query.answer(inline_results, cache_time=1)

    except Exception as e:
        # Handle errors (e.g., API failure)
        await inline_query.answer(
            [InlineQueryResultArticle(
                id="error",
                title="Error",
                input_message_content=InputTextMessageContent(f"Failed to search: {str(e)}")
            )],
            cache_time=1
        )

# Start command for basic interaction
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply("Hi! Use me in inline mode by typing `@YourBotName query` to search for videos.")

# Run the bot
if __name__ == "__main__":
    print("Bot is running...")
    app.run()
