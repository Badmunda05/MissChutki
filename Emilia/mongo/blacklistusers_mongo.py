from Emilia import db

bluser_col = db["blacklist_users"]


async def add_bluser(user_id: int, reason: str = ""):
    await bluser_col.update_one(
        {"uid": user_id},
        {"$set": {"uid": user_id, "reason": reason}},
        upsert=True,
    )


async def remove_bluser(user_id: int):
    await bluser_col.delete_one({"uid": user_id})


async def is_bluser(user_id: int) -> bool:
    return bool(await bluser_col.find_one({"uid": user_id}))


async def get_bluserlist() -> list:
    return [d async for d in bluser_col.find({})]
