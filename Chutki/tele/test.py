from Chutki.custom_filter import register
from Chutki.utils.decorators import *


@register(pattern="test")
@rate_limit(RATE_LIMIT_GENERAL)
async def test(event):
    await event.reply("test")