import asyncio
import speedtest as sptest

from Emilia.custom_filter import register

__mod_name__ = "Speed Test"
__help__ = """
• `/speedtest` — Check the bot server's internet speed.
"""


@register(pattern="speedtest")
async def speedtest_cmd(event):
    msg = await event.reply("🔄 Running speed test, please wait...")
    try:
        loop = asyncio.get_event_loop()
        st = await loop.run_in_executor(None, _run_speedtest)
        await msg.edit(
            f"**🚀 Speed Test Results:**\n\n"
            f"📥 **Download:** {st['download']} Mbps\n"
            f"📤 **Upload:** {st['upload']} Mbps\n"
            f"📡 **Ping:** {st['ping']} ms\n"
            f"🌐 **Server:** {st['server']}"
        )
    except Exception as e:
        await msg.edit(f"❌ Speed test failed: {e}")


def _run_speedtest():
    s = sptest.Speedtest()
    s.get_best_server()
    s.download()
    s.upload()
    res = s.results.dict()
    return {
        "download": round(res["download"] / 1_000_000, 2),
        "upload": round(res["upload"] / 1_000_000, 2),
        "ping": round(res["ping"], 2),
        "server": res["server"]["name"] + ", " + res["server"]["country"],
    }
