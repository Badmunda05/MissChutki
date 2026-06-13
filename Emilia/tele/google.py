import aiohttp
from bs4 import BeautifulSoup
from telethon import events

from Emilia.custom_filter import register

__mod_name__ = "Google"
__help__ = """
• `/google` [query] — Search Google and get top results.
• `/img` [query] — Search Google Images and send a photo.
• `/reverse` — Reply to a photo/sticker to do reverse image search.
• `/app` [app name] — Search Google Play Store for an app.

**Examples:**
`/google Python tutorials`
`/img cute cats`
`/app WhatsApp`
"""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36"
}


async def _google_search(query: str, num: int = 5) -> list:
    """Returns list of (title, url, snippet) dicts."""
    url = f"https://www.google.com/search?q={query}&num={num}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            html = await resp.text()

    soup = BeautifulSoup(html, "html.parser")
    results = []
    for g in soup.select("div.g")[:num]:
        title_tag = g.select_one("h3")
        link_tag = g.select_one("a")
        snippet_tag = g.select_one("div.VwiC3b") or g.select_one("span.aCOpRe")
        if title_tag and link_tag:
            results.append({
                "title": title_tag.get_text(),
                "url": link_tag.get("href", ""),
                "snippet": snippet_tag.get_text() if snippet_tag else "",
            })
    return results


@register(pattern="google(?: (.+))?")
async def google_cmd(event):
    match = event.pattern_match.group(1)
    if not match:
        return await event.reply("**Usage:** `/google your query`")

    query = match.strip()
    msg = await event.reply(f"🔍 Searching Google for: **{query}**...")

    try:
        results = await _google_search(query)
        if not results:
            return await msg.edit("❌ No results found.")

        text = f"🔍 **Google Results for:** `{query}`\n\n"
        for i, r in enumerate(results, 1):
            text += f"**{i}. [{r['title']}]({r['url']})**\n"
            if r["snippet"]:
                text += f"_{r['snippet'][:100]}_\n"
            text += "\n"

        await msg.edit(text, link_preview=False)

    except Exception as e:
        await msg.edit(f"❌ Search failed: {e}")


@register(pattern="img(?: (.+))?")
async def img_search(event):
    match = event.pattern_match.group(1)
    if not match:
        return await event.reply("**Usage:** `/img cats`")

    query = match.strip()
    msg = await event.reply(f"🖼 Searching images for: **{query}**...")

    try:
        url = f"https://www.google.com/search?tbm=isch&q={query}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        # Find image URLs from the page
        img_tags = soup.find_all("img")
        img_urls = []
        for tag in img_tags:
            src = tag.get("src") or tag.get("data-src")
            if src and src.startswith("http") and "gstatic" not in src:
                img_urls.append(src)
            if len(img_urls) >= 3:
                break

        if not img_urls:
            # Fallback: try Unsplash
            unsplash = f"https://source.unsplash.com/800x600/?{query.replace(' ', ',')}"
            await msg.delete()
            await event.reply(f"**🖼 Image:** `{query}`", file=unsplash)
            return

        await msg.delete()
        await event.reply(
            f"**🖼 Image results for:** `{query}`",
            file=img_urls[0]
        )

    except Exception as e:
        await msg.edit(f"❌ Image search failed: {e}")


@register(pattern="reverse")
async def reverse_img(event):
    if not event.reply_to_message:
        return await event.reply("Reply to a photo or sticker to reverse search it.")

    reply = event.reply_to_message
    if not (reply.photo or reply.sticker or reply.document):
        return await event.reply("I can only reverse search images or stickers.")

    msg = await event.reply("🔍 Doing reverse image search...")

    try:
        file = await reply.download_media()
        if not file:
            return await msg.edit("❌ Could not download the image.")

        async with aiohttp.ClientSession() as session:
            with open(file, "rb") as f:
                data = aiohttp.FormData()
                data.add_field("encoded_image", f, filename="image.jpg", content_type="image/jpeg")
                async with session.post(
                    "https://www.google.com/searchbyimage/upload",
                    data=data,
                    headers={"User-Agent": HEADERS["User-Agent"]},
                    allow_redirects=True,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    final_url = str(resp.url)

        import os
        os.remove(file)

        await msg.edit(
            f"🔍 **Reverse Image Search Result:**\n{final_url}",
            link_preview=False
        )

    except Exception as e:
        await msg.edit(f"❌ Reverse search failed: {e}")


@register(pattern="app(?: (.+))?")
async def app_search(event):
    match = event.pattern_match.group(1)
    if not match:
        return await event.reply("**Usage:** `/app WhatsApp`")

    query = match.strip()
    msg = await event.reply(f"📱 Searching Play Store for: **{query}**...")

    try:
        search_url = f"https://play.google.com/store/search?q={query}&c=apps"
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        app = soup.select_one("div.VfPpkd-WsjYwc")
        if not app:
            return await msg.edit("❌ No app found.")

        name = app.select_one("span.DdYX5") or app.select_one("span")
        dev = app.select_one("div.wMUdtb")
        link_tag = app.select_one("a[href*='/store/apps/details']")

        name_text = name.get_text() if name else query
        dev_text = dev.get_text() if dev else "Unknown"
        link = "https://play.google.com" + link_tag["href"] if link_tag else search_url

        await msg.edit(
            f"📱 **{name_text}**\n"
            f"👨‍💻 **Developer:** {dev_text}\n"
            f"🔗 [Play Store]({link})",
            link_preview=False
        )

    except Exception as e:
        await msg.edit(f"❌ App search failed: {e}")
