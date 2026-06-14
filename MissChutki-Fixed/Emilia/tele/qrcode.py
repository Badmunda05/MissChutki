import io
import qrcode
from telethon import events

from Emilia.custom_filter import register

__mod_name__ = "QR Code"
__help__ = """
• `/qr` [text/url] — Generate a QR code for any text or URL.
**Example:** `/qr https://t.me/yourbot`
"""


@register(pattern="qr(?: (.+))?")
async def qr_cmd(event):
    match = event.pattern_match.group(1)
    if not match:
        if event.reply_to_message and event.reply_to_message.text:
            match = event.reply_to_message.text
        else:
            return await event.reply("Provide text or reply to a message.\n**Usage:** `/qr your text here`")

    text = match.strip()

    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        bio = io.BytesIO()
        bio.name = "qrcode.png"
        img.save(bio, "PNG")
        bio.seek(0)

        await event.reply(file=bio, message="📷 **QR Code generated!**")

    except Exception as e:
        await event.reply(f"❌ Failed to generate QR code: {e}")
