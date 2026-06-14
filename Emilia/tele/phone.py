import aiohttp
from Emilia.custom_filter import register

__mod_name__ = "Phone"
__help__ = """
• `/phone` [number] — Look up a phone number.
**Example:** `/phone +91XXXXXXXXXX`
"""


@register(pattern="phone(?: (.+))?")
async def phone_cmd(event):
    match = event.pattern_match.group(1)
    if not match:
        return await event.reply("**Usage:** `/phone +91XXXXXXXXXX`")

    number = match.strip().replace(" ", "")

    try:
        import phonenumbers
        from phonenumbers import geocoder, carrier, timezone

        parsed = phonenumbers.parse(number)
        is_valid = phonenumbers.is_valid_number(parsed)

        if not is_valid:
            return await event.reply("❌ Invalid phone number. Include country code e.g. `+91`.")

        country = geocoder.description_for_number(parsed, "en")
        op = carrier.name_for_number(parsed, "en")
        tz_list = timezone.time_zones_for_number(parsed)
        tz_str = ", ".join(tz_list) if tz_list else "N/A"
        num_type = phonenumbers.number_type(parsed)
        type_map = {
            0: "Fixed Line", 1: "Mobile", 2: "Fixed or Mobile",
            3: "Toll Free", 4: "Premium Rate", 6: "Voip", 99: "Unknown"
        }

        await event.reply(
            f"📱 **Phone Number Info:**\n\n"
            f"🔢 **Number:** `{number}`\n"
            f"✅ **Valid:** {'Yes' if is_valid else 'No'}\n"
            f"🌍 **Country:** {country}\n"
            f"📡 **Carrier:** {op or 'N/A'}\n"
            f"🕐 **Timezone:** {tz_str}\n"
            f"📞 **Type:** {type_map.get(num_type, 'Unknown')}"
        )

    except ImportError:
        await event.reply("❌ `phonenumbers` library not installed.")
    except Exception as e:
        await event.reply(f"❌ Error: {e}")
