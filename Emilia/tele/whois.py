import aiohttp
from Emilia.custom_filter import register

__mod_name__ = "Whois"
__help__ = """
• `/whois` [domain/IP] — Look up domain or IP info.
**Example:** `/whois google.com` or `/whois 8.8.8.8`
"""


@register(pattern="whois(?: (.+))?")
async def whois_cmd(event):
    match = event.pattern_match.group(1)
    if not match:
        return await event.reply("**Usage:** `/whois google.com` or `/whois 8.8.8.8`")

    query = match.strip()

    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://ipwho.is/{query}"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json()

        if not data.get("success", True) and "ip" not in data:
            return await event.reply(f"❌ Could not find info for `{query}`")

        result = (
            f"**🌐 Whois/IP Lookup:** `{query}`\n\n"
            f"🏳️ **Country:** {data.get('country', 'N/A')} ({data.get('country_code', 'N/A')})\n"
            f"🏙 **City:** {data.get('city', 'N/A')}\n"
            f"📍 **Region:** {data.get('region', 'N/A')}\n"
            f"🌍 **Continent:** {data.get('continent', 'N/A')}\n"
            f"🏢 **ISP/Org:** {data.get('org', 'N/A')}\n"
            f"📡 **Timezone:** {data.get('timezone', {}).get('id', 'N/A') if isinstance(data.get('timezone'), dict) else data.get('timezone', 'N/A')}"
        )
        await event.reply(result)

    except Exception as e:
        await event.reply(f"❌ Error: {e}")
