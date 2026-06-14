import base64
import binascii

from Emilia.custom_filter import register

__mod_name__ = "Encode/Decode"
__help__ = """
• `/encode` [text] — Encode text to Base64.
• `/decode` [text] — Decode text from Base64.
**Example:** `/encode Hello World`
"""


@register(pattern="encode(?: (.+))?")
async def encode_cmd(event):
    match = event.pattern_match.group(1)
    if not match:
        if event.reply_to_message and event.reply_to_message.text:
            match = event.reply_to_message.text
        else:
            return await event.reply("Provide text to encode.\n**Usage:** `/encode your text`")

    encoded = base64.b64encode(match.strip().encode()).decode()
    await event.reply(f"**🔒 Encoded (Base64):**\n`{encoded}`")


@register(pattern="decode(?: (.+))?")
async def decode_cmd(event):
    match = event.pattern_match.group(1)
    if not match:
        if event.reply_to_message and event.reply_to_message.text:
            match = event.reply_to_message.text
        else:
            return await event.reply("Provide text to decode.\n**Usage:** `/decode encoded_text`")

    try:
        decoded = base64.b64decode(match.strip().encode()).decode()
        await event.reply(f"**🔓 Decoded:**\n`{decoded}`")
    except (binascii.Error, UnicodeDecodeError):
        await event.reply("❌ Invalid Base64 string.")
