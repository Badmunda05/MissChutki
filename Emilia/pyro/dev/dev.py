"""
Developer commands for MissChutki — adapted from GcManagement Dev.py + Restart.py
"""
import asyncio, os, re, shutil, subprocess, sys, traceback
from datetime import datetime
from io import StringIO
from inspect import getfullargspec
from time import time

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from Emilia import OWNER_ID, DEV_USERS, UPSTREAM_REPO, UPSTREAM_BRANCH, GIT_TOKEN, custom_filter
from Emilia.mongo.disasters_mongo import is_dragon, is_demon

__mod_name__ = "Developer"
__help__ = """
**⚙️ Developer Commands** — Owner/Sudo only

• `/eval` — Run Python code live.
• `/sh` — Run Linux shell commands. Example: `/sh git status`
• `/update` or `/gitpull` — Check & pull updates from upstream repo, then restart.
• `/restart` — Restart the bot.
• `/logs` — Get bot log file.
• `/broadcast` — Reply to any message + send this to broadcast it to all groups.
• `/vars` — View current bot config values.
• `/stats` — Bot stats (total chats & users).
"""


async def _is_sudo(uid: int) -> bool:
    return uid == OWNER_ID or uid in DEV_USERS or await is_dragon(uid) or await is_demon(uid)


# ─── EVAL ──────────────────────────────────────────────────────────────────────

async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {line}" for line in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


@Client.on_message(custom_filter.command(commands=["eval", "ev"]))
async def executor(client: Client, message: Message):
    if not await _is_sudo(message.from_user.id):
        return
    if len(message.command) < 2:
        return await message.reply("<b>Usage:</b> <code>/eval print('hello')</code>")

    cmd = message.text.split(None, 1)[1]
    t1 = time()
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = buf = StringIO()
    exc = None
    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()
    output = buf.getvalue()
    sys.stdout, sys.stderr = old_stdout, old_stderr

    result = exc or output or "✅ Success (no output)"
    t2 = time()

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton(f"⏳ {round(t2-t1,3)}s", callback_data=f"dev_rt_{round(t2-t1,3)}"),
        InlineKeyboardButton("🗑 Close", callback_data=f"dev_close_{message.from_user.id}"),
    ]])

    final = f"<b>⥤ Result:</b>\n<pre language='python'>{result}</pre>"
    if len(final) > 4096:
        fname = "eval_out.txt"
        with open(fname, "w", encoding="utf8") as f:
            f.write(result)
        await message.reply_document(fname, caption=f"<code>{cmd[:200]}</code>")
        os.remove(fname)
    else:
        await message.reply(final, reply_markup=kb)


@Client.on_callback_query(filters.regex(r"^dev_rt_"))
async def eval_runtime(_, cq):
    await cq.answer(f"Execution time: {cq.data.split('_',2)[2]} seconds", show_alert=True)


@Client.on_callback_query(filters.regex(r"^dev_close_(\d+)$"))
async def eval_close(_, cq):
    if cq.from_user.id != int(cq.data.split("_")[2]):
        return await cq.answer("Not for you!", show_alert=True)
    await cq.message.delete()


# ─── SHELL ─────────────────────────────────────────────────────────────────────

@Client.on_message(custom_filter.command(commands=["sh", "shell"]))
async def shell_cmd(_, message: Message):
    if not await _is_sudo(message.from_user.id):
        return
    if len(message.command) < 2:
        return await message.reply("<b>Usage:</b> <code>/sh git pull</code>")

    cmd = message.text.split(None, 1)[1]
    msg = await message.reply(f"<code>$ {cmd}</code>\n⏳ Running...")
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
        out = (stdout.decode("utf-8", "replace") + stderr.decode("utf-8", "replace")).strip() or "✅ Done."
    except asyncio.TimeoutError:
        return await msg.edit("❌ Timed out (60s).")
    except Exception as e:
        return await msg.edit(f"❌ Error: {e}")

    if len(out) > 4000:
        with open("sh_out.txt", "w", encoding="utf8") as f:
            f.write(out)
        await message.reply_document("sh_out.txt", caption=f"<code>$ {cmd[:200]}</code>")
        os.remove("sh_out.txt")
        await msg.delete()
    else:
        await msg.edit(f"<code>$ {cmd}</code>\n\n<pre>{out}</pre>")


# ─── GITPULL / UPDATE ──────────────────────────────────────────────────────────

@Client.on_message(custom_filter.command(commands=["update", "gitpull"]))
async def update_cmd(_, message: Message):
    if not await _is_sudo(message.from_user.id):
        return

    resp = await message.reply("🔄 Checking for updates...")

    try:
        repo = Repo()
    except InvalidGitRepositoryError:
        return await resp.edit(
            f"❌ Not a git repo.\nClone properly:\n<code>git clone {UPSTREAM_REPO}</code>"
        )
    except GitCommandError as e:
        return await resp.edit(f"❌ Git error: <code>{e}</code>")

    upstream_url = UPSTREAM_REPO
    if GIT_TOKEN:
        try:
            domain = UPSTREAM_REPO.split("https://")[1]
            user = domain.split("/")[0]
            upstream_url = f"https://{user}:{GIT_TOKEN}@{domain}"
        except Exception:
            pass

    os.system(f"git fetch origin {UPSTREAM_BRANCH} &>/dev/null")
    await asyncio.sleep(4)

    commits = list(repo.iter_commits(f"HEAD..origin/{UPSTREAM_BRANCH}"))
    if not commits:
        return await resp.edit("✅ Bot is already up-to-date!")

    REPO_URL = repo.remotes.origin.url.split(".git")[0]
    ordinal = lambda n: "%d%s" % (n, "tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

    updates = ""
    for c in commits:
        dt = datetime.fromtimestamp(c.committed_date)
        updates += (
            f"• <a href='{REPO_URL}/commit/{c}'>{c.summary}</a> "
            f"by <b>{c.author}</b> — "
            f"{ordinal(int(dt.strftime('%d')))} {dt.strftime('%b %Y')}\n"
        )

    text = f"🆕 <b>{len(commits)} update(s) found!</b>\n\n{updates}"
    if len(text) > 4000:
        text = f"🆕 <b>{len(commits)} update(s) found!</b>\n\nPulling now..."

    await resp.edit(text, disable_web_page_preview=True)

    os.system("git stash &>/dev/null && git pull")
    await asyncio.sleep(2)
    os.system("pip3 install -r requirements.txt -q")
    await resp.edit(text + "\n\n✅ <b>Updated! Restarting...</b>")
    os.execv(sys.executable, [sys.executable, "-m", "Emilia"])


# ─── RESTART ───────────────────────────────────────────────────────────────────

@Client.on_message(custom_filter.command(commands=["restart"]))
async def restart_cmd(_, message: Message):
    if not await _is_sudo(message.from_user.id):
        return
    await message.reply("🔄 Restarting MissChutki... ~15 seconds.")
    for d in ["downloads", "raw_files", "cache", "__pycache__"]:
        try:
            shutil.rmtree(d)
        except Exception:
            pass
    await asyncio.sleep(1)
    os.execv(sys.executable, [sys.executable, "-m", "Emilia"])


# ─── LOGS ──────────────────────────────────────────────────────────────────────

@Client.on_message(custom_filter.command(commands=["logs", "getlogs", "getlog"]))
async def logs_cmd(_, message: Message):
    if not await _is_sudo(message.from_user.id):
        return
    try:
        await message.reply_document("log.txt", caption="📋 Bot Logs")
    except FileNotFoundError:
        await message.reply("❌ No `log.txt` found.")
    except Exception as e:
        await message.reply(f"❌ {e}")


# ─── BROADCAST ─────────────────────────────────────────────────────────────────

@Client.on_message(custom_filter.command(commands=["broadcast", "bc"]))
async def broadcast_cmd(client: Client, message: Message):
    if not await _is_sudo(message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply("Reply to a message to broadcast it to all groups.")

    from Emilia.mongo.users_mongo import chats
    msg = await message.reply("📣 Broadcasting...")
    sent = failed = 0

    async for doc in chats.find({}):
        chat_id = doc.get("chat_id")
        if not chat_id:
            continue
        try:
            await message.reply_to_message.copy(chat_id)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    await msg.edit(f"📣 **Broadcast Done!**\n✅ Sent: {sent}\n❌ Failed: {failed}")


# ─── VARS ──────────────────────────────────────────────────────────────────────

@Client.on_message(custom_filter.command(commands=["vars", "config"]))
async def vars_cmd(_, message: Message):
    if not await _is_sudo(message.from_user.id):
        return
    from Emilia import API_ID, BOT_USERNAME, BOT_ID, EVENT_LOGS, OWNER_ID, UPSTREAM_REPO, UPSTREAM_BRANCH, SUPPORT_CHAT, UPDATE_CHANNEL
    await message.reply(
        "<b>⚙️ Bot Config:</b>\n\n"
        f"<b>API_ID:</b> <code>{API_ID}</code>\n"
        f"<b>BOT_ID:</b> <code>{BOT_ID}</code>\n"
        f"<b>BOT_USERNAME:</b> @{BOT_USERNAME}\n"
        f"<b>OWNER_ID:</b> <code>{OWNER_ID}</code>\n"
        f"<b>EVENT_LOGS:</b> <code>{EVENT_LOGS}</code>\n"
        f"<b>UPSTREAM_REPO:</b> {UPSTREAM_REPO}\n"
        f"<b>UPSTREAM_BRANCH:</b> <code>{UPSTREAM_BRANCH}</code>\n"
        f"<b>SUPPORT_CHAT:</b> @{SUPPORT_CHAT}\n"
        f"<b>UPDATE_CHANNEL:</b> @{UPDATE_CHANNEL}\n"
    )


# ─── STATS ─────────────────────────────────────────────────────────────────────

@Client.on_message(custom_filter.command(commands=["stats"]))
async def stats_cmd(_, message: Message):
    if not await _is_sudo(message.from_user.id):
        return
    from Emilia.mongo.users_mongo import chats, users
    total_chats = await chats.count_documents({})
    total_users = await users.count_documents({})
    await message.reply(
        f"📊 <b>Bot Stats:</b>\n\n"
        f"👥 <b>Total Groups:</b> <code>{total_chats}</code>\n"
        f"👤 <b>Total Users:</b> <code>{total_users}</code>"
    )
