import aiohttp
from telethon import events

from Emilia import telethn
from Emilia.custom_filter import register

__mod_name__ = "Weather"
__help__ = """
• `/weather` [city] — Get current weather for a city.
**Example:** `/weather Mumbai`
"""


@register(pattern="weather(?: (.+))?")
async def weather_cmd(event):
    match = event.pattern_match.group(1)
    if not match:
        return await event.reply("Please provide a city name.\n**Usage:** `/weather Mumbai`")

    city = match.strip()
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://wttr.in/{city}?format=4"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return await event.reply("❌ Could not get weather. Check the city name.")
                data = await resp.text()

        await event.reply(f"🌤 **Weather for {city}:**\n`{data}`")

    except Exception as e:
        await event.reply(f"❌ Error: {e}")
