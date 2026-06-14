import aiohttp
from Emilia.custom_filter import register

__mod_name__ = "Paste"
__help__ = """
• `/paste` — Reply to a text message to paste it on Hastebin.
"""


@register(pattern="paste")
async def paste_cmd(event):
    if not event.reply_to_message:
        return await event.reply("Reply to a text message to paste it.")

    text = event.reply_to_message.text or event.reply_to_message.caption
    if not text:
        return await event.reply("I can only paste text messages.")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://hastebin.com/documents",
                data=text.encode("utf-8"),
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                result = await resp.json()

        key = result.get("key")
        if not key:
            return await event.reply("❌ Failed to paste. Try again.")

        url = f"https://hastebin.com/{key}"
        await event.reply(f"📋 **Pasted!**\n{url}")

    except Exception as e:
        await event.reply(f"❌ Error: {e}")
