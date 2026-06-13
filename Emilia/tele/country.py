import aiohttp
from Emilia.custom_filter import register

__mod_name__ = "Country Info"
__help__ = """
• `/country` [country name or code] — Get information about a country.
**Example:** `/country India` or `/country US`
"""


@register(pattern="country(?: (.+))?")
async def country_cmd(event):
    match = event.pattern_match.group(1)
    if not match:
        return await event.reply("**Usage:** `/country India`")

    query = match.strip()

    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://restcountries.com/v3.1/name/{query}?fullText=true"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 404:
                    # Try partial
                    url2 = f"https://restcountries.com/v3.1/name/{query}"
                    async with session.get(url2, timeout=aiohttp.ClientTimeout(total=10)) as resp2:
                        if resp2.status != 200:
                            return await event.reply(f"❌ Country `{query}` not found.")
                        data = (await resp2.json())[0]
                elif resp.status == 200:
                    data = (await resp.json())[0]
                else:
                    return await event.reply(f"❌ Country `{query}` not found.")

        name = data["name"]["common"]
        official = data["name"]["official"]
        capital = ", ".join(data.get("capital", ["N/A"]))
        region = data.get("region", "N/A")
        sub = data.get("subregion", "N/A")
        pop = f"{data.get('population', 0):,}"
        area = f"{data.get('area', 0):,} km²"
        langs = ", ".join(data.get("languages", {}).values()) or "N/A"
        currencies = ", ".join(
            f"{v['name']} ({v.get('symbol', '')})" for v in data.get("currencies", {}).values()
        ) or "N/A"
        flag = data.get("flag", "")

        text = (
            f"{flag} **{name}** (`{official}`)\n\n"
            f"🏙 **Capital:** {capital}\n"
            f"🌍 **Region:** {region} / {sub}\n"
            f"👥 **Population:** {pop}\n"
            f"📐 **Area:** {area}\n"
            f"🗣 **Languages:** {langs}\n"
            f"💰 **Currency:** {currencies}"
        )
        await event.reply(text)

    except Exception as e:
        await event.reply(f"❌ Error: {e}")
