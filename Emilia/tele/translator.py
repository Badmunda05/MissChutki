import aiohttp
from telethon import events

from Emilia.custom_filter import register

__mod_name__ = "Translator"
__help__ = """
• `/tr` [lang_code] — Reply to a message to translate it.
**Example:** `/tr en` — Translate to English
**Example:** `/tr hi` — Translate to Hindi
"""


@register(pattern="tr(?: (.+))?")
async def translate_cmd(event):
    if not event.reply_to_message:
        return await event.reply("Reply to a message to translate it.\n**Usage:** Reply + `/tr en`")

    match = event.pattern_match.group(1)
    dest = match.strip() if match else "en"

    text = event.reply_to_message.text or event.reply_to_message.caption
    if not text:
        return await event.reply("I can only translate text messages.")

    try:
        async with aiohttp.ClientSession() as session:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": "auto",
                "tl": dest,
                "dt": "t",
                "q": text,
            }
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                result = await resp.json()

        translated = "".join([item[0] for item in result[0] if item[0]])
        src_lang = result[2] if len(result) > 2 else "auto"

        await event.reply(
            f"🌐 **Translated** ({src_lang} → {dest}):\n\n{translated}"
        )

    except Exception as e:
        await event.reply(f"❌ Translation failed: {e}")
