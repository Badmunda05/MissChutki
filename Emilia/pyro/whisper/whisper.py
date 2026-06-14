from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    InlineQueryResultArticle, InputTextMessageContent,
)
from Emilia import BOT_USERNAME, OWNER_ID, custom_filter

__mod_name__ = "Whisper"
__help__ = """
**💌 Whisper** — Send secret inline messages

Inline mode mein use karo:
`@BotUsername @target_user secret message`

Target user ko ek button milega — sirf woh padh sakta hai.
**One-time whisper** — padhne ke baad delete ho jaata hai.
"""

_db: dict = {}

_switch = InlineKeyboardMarkup([[InlineKeyboardButton("💌 Start Whisper", switch_inline_query_current_chat="")]])


@Client.on_inline_query()
async def whisper_inline(client: Client, iq):
    query = iq.query.strip()
    bot = BOT_USERNAME

    if not query or len(query.split()) < 2:
        return await iq.answer([
            InlineQueryResultArticle(
                title="💌 Whisper",
                description=f"@{bot} @username Your secret message",
                input_message_content=InputTextMessageContent(
                    f"**💌 Usage:**\n`@{bot} @username your secret message`"
                ),
                reply_markup=_switch,
            )
        ], cache_time=0)

    parts = query.split(None, 1)
    target_raw, text = parts[0].lstrip("@"), parts[1]

    try:
        target = await client.get_users(target_raw)
    except Exception:
        return await iq.answer([
            InlineQueryResultArticle(
                title="❌ User not found",
                description=f"Can't find @{target_raw}",
                input_message_content=InputTextMessageContent(f"User @{target_raw} not found."),
            )
        ], cache_time=0)

    from_id, to_id = iq.from_user.id, target.id
    _db[f"{from_id}_{to_id}"] = text
    tname = target.first_name or target_raw

    await iq.answer([
        InlineQueryResultArticle(
            title=f"💌 Whisper to {tname}",
            description="Only they can read it!",
            input_message_content=InputTextMessageContent(
                f"💌 **{iq.from_user.first_name}** sent a whisper to **{tname}**.\nOnly they can read it!"
            ),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💌 Read Whisper", callback_data=f"wsp_{from_id}_{to_id}")
            ]]),
        ),
        InlineQueryResultArticle(
            title=f"🔐 One-Time Whisper to {tname}",
            description="Deleted after reading once.",
            input_message_content=InputTextMessageContent(
                f"🔐 **{iq.from_user.first_name}** sent a one-time whisper to **{tname}**."
            ),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔐 Read Once", callback_data=f"wsp1_{from_id}_{to_id}")
            ]]),
        ),
    ], cache_time=0)


@Client.on_callback_query(filters.regex(r"^wsp_(\d+)_(\d+)$"))
async def wsp_read(_, cq):
    _, from_id, to_id = cq.data.split("_")
    from_id, to_id = int(from_id), int(to_id)
    if cq.from_user.id not in [from_id, to_id, OWNER_ID]:
        return await cq.answer("🚫 This whisper is not for you!", show_alert=True)
    msg = _db.get(f"{from_id}_{to_id}", "⚠️ Whisper expired.")
    await cq.answer(msg, show_alert=True)


@Client.on_callback_query(filters.regex(r"^wsp1_(\d+)_(\d+)$"))
async def wsp_read_once(_, cq):
    _, from_id, to_id = cq.data.split("_")
    from_id, to_id = int(from_id), int(to_id)
    if cq.from_user.id not in [from_id, to_id, OWNER_ID]:
        return await cq.answer("🚫 This whisper is not for you!", show_alert=True)
    msg = _db.pop(f"{from_id}_{to_id}", "⚠️ Already read or expired.")
    await cq.answer(msg, show_alert=True)
    if cq.from_user.id == to_id:
        try:
            await cq.message.edit_text("📭 Whisper read & deleted.")
        except Exception:
            pass
