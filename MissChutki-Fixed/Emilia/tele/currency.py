import aiohttp
from Emilia.custom_filter import register

__mod_name__ = "Currency"
__help__ = """
• `/currency` [amount] [from] [to] — Convert currency.
**Example:** `/currency 100 USD INR`
"""


@register(pattern="currency(?: (.+))?")
async def currency_cmd(event):
    match = event.pattern_match.group(1)
    if not match:
        return await event.reply("**Usage:** `/currency 100 USD INR`")

    args = match.strip().split()
    if len(args) < 3:
        return await event.reply("**Usage:** `/currency 100 USD INR`")

    try:
        amount = float(args[0])
        from_cur = args[1].upper()
        to_cur = args[2].upper()
    except ValueError:
        return await event.reply("❌ Invalid amount. **Usage:** `/currency 100 USD INR`")

    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://open.er-api.com/v6/latest/{from_cur}"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json()

        if data.get("result") != "success":
            return await event.reply("❌ Could not fetch exchange rates. Check currency codes.")

        rate = data["rates"].get(to_cur)
        if not rate:
            return await event.reply(f"❌ Currency `{to_cur}` not found.")

        converted = amount * rate
        await event.reply(
            f"💱 **Currency Conversion:**\n\n"
            f"`{amount:.2f} {from_cur}` = **`{converted:.2f} {to_cur}`**\n"
            f"Rate: 1 {from_cur} = {rate:.4f} {to_cur}"
        )

    except Exception as e:
        await event.reply(f"❌ Error: {e}")
