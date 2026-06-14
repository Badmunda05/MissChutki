import aiohttp, os, shutil
from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from Emilia import custom_filter

__mod_name__ = "GitHub"
__help__ = """
• `/git` [username] — GitHub user info with profile picture.
• `/downloadrepo` [url] — Download a public GitHub repo as zip.

**Examples:**
`/git torvalds`
`/downloadrepo https://github.com/user/repo`
"""


@Client.on_message(custom_filter.command(commands=["git", "github"]))
async def github_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("**Usage:** `/git username`")

    username = message.command[1].lstrip("@")
    msg = await message.reply(f"🔍 Fetching `{username}`...")

    async with aiohttp.ClientSession() as s:
        async with s.get(f"https://api.github.com/users/{username}",
                         headers={"Accept": "application/vnd.github.v3+json"},
                         timeout=aiohttp.ClientTimeout(total=10)) as r:
            if r.status == 404:
                return await msg.edit(f"❌ User `{username}` not found on GitHub.")
            data = await r.json()

    caption = (
        f"**👨‍💻 [{data.get('name') or username}](https://github.com/{username})**\n\n"
        f"👤 **Username:** `{data.get('login')}`\n"
        f"📝 **Bio:** {data.get('bio') or 'N/A'}\n"
        f"🏢 **Company:** {data.get('company') or 'N/A'}\n"
        f"📍 **Location:** {data.get('location') or 'N/A'}\n"
        f"🌐 **Blog:** {data.get('blog') or 'N/A'}\n"
        f"📦 **Repos:** {data.get('public_repos', 0)}\n"
        f"👥 **Followers:** {data.get('followers', 0)}\n"
        f"👣 **Following:** {data.get('following', 0)}\n"
        f"📅 **Joined:** {data.get('created_at', '')[:10]}"
    )

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("🔗 GitHub Profile", url=f"https://github.com/{username}"),
        InlineKeyboardButton("🗑 Close", callback_data="gh_close"),
    ]])

    try:
        await msg.delete()
        await message.reply_photo(data["avatar_url"], caption=caption, reply_markup=kb)
    except Exception:
        await message.reply(caption, reply_markup=kb, disable_web_page_preview=True)


@Client.on_message(custom_filter.command(commands=["downloadrepo"]))
async def download_repo_cmd(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("**Usage:** `/downloadrepo https://github.com/user/repo`")

    url = message.command[1].rstrip("/")
    if "github.com" not in url:
        return await message.reply("❌ Only GitHub URLs supported.")

    repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
    msg = await message.reply(f"📥 Cloning `{repo_name}`...")

    try:
        clone_path = f"/tmp/{repo_name}"
        zip_path = f"/tmp/{repo_name}.zip"
        for p in [clone_path, zip_path]:
            if os.path.exists(p):
                shutil.rmtree(p, ignore_errors=True)
                try: os.remove(p)
                except: pass

        import subprocess
        r = subprocess.run(["git", "clone", "--depth=1", url, clone_path],
                           capture_output=True, timeout=60)
        if r.returncode != 0:
            return await msg.edit(f"❌ Clone failed:\n`{r.stderr.decode()[:300]}`")

        shutil.make_archive(f"/tmp/{repo_name}", "zip", clone_path)
        shutil.rmtree(clone_path, ignore_errors=True)

        await msg.delete()
        await message.reply_document(zip_path, caption=f"📦 `{repo_name}.zip`\n{url}")
        os.remove(zip_path)
    except subprocess.TimeoutExpired:
        await msg.edit("❌ Timed out — repo too large?")
    except Exception as e:
        await msg.edit(f"❌ Error: {e}")


from pyrogram import filters as pyro_filters
@Client.on_callback_query(pyro_filters.regex(r"^gh_close$"))
async def gh_close(_, cq):
    await cq.message.delete()
