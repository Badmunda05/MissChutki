from Emilia import db

blsticker_col = db["blacklist_stickers"]


async def add_to_blacklist(chat_id: int, set_name: str):
    await blsticker_col.update_one(
        {"chat_id": chat_id, "set": set_name},
        {"$set": {"chat_id": chat_id, "set": set_name}},
        upsert=True,
    )


async def remove_from_blacklist(chat_id: int, set_name: str):
    await blsticker_col.delete_one({"chat_id": chat_id, "set": set_name})


async def get_blacklisted_stickers(chat_id: int) -> list:
    return [d["set"] async for d in blsticker_col.find({"chat_id": chat_id})]


async def is_sticker_blacklisted(chat_id: int, set_name: str) -> bool:
    return bool(await blsticker_col.find_one({"chat_id": chat_id, "set": set_name}))


async def get_bl_sticker_mode(chat_id: int) -> str:
    doc = await blsticker_col.find_one({"chat_id": chat_id, "mode": {"$exists": True}})
    return doc.get("mode", "del") if doc else "del"


async def set_bl_sticker_mode(chat_id: int, mode: str):
    await blsticker_col.update_one(
        {"chat_id": chat_id, "mode": {"$exists": True}},
        {"$set": {"chat_id": chat_id, "mode": mode}},
        upsert=True,
    )
