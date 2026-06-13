from Emilia import db

fsub_col = db["fsub"]


async def set_fsub(chat_id: int, channel: str):
    await fsub_col.update_one(
        {"chat_id": chat_id},
        {"$set": {"chat_id": chat_id, "channel": channel}},
        upsert=True,
    )


async def get_fsub(chat_id: int):
    return await fsub_col.find_one({"chat_id": chat_id})


async def del_fsub(chat_id: int):
    await fsub_col.delete_one({"chat_id": chat_id})
