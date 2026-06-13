from Emilia import db

gban_col = db["gbans"]
gmute_col = db["gmutes"]


# ─── GBAN ────────────────────────────────────────────────────────────────────

async def add_gban(user_id: int, reason: str = "", banned_by: int = 0):
    await gban_col.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, "reason": reason, "banned_by": banned_by}},
        upsert=True,
    )


async def remove_gban(user_id: int):
    await gban_col.delete_one({"user_id": user_id})


async def is_gbanned(user_id: int) -> bool:
    return bool(await gban_col.find_one({"user_id": user_id}))


async def get_gban(user_id: int):
    return await gban_col.find_one({"user_id": user_id})


async def get_gban_list():
    return [doc async for doc in gban_col.find({})]


async def gban_count() -> int:
    return await gban_col.count_documents({})


# ─── GMUTE ───────────────────────────────────────────────────────────────────

async def add_gmute(user_id: int, reason: str = "", muted_by: int = 0):
    await gmute_col.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, "reason": reason, "muted_by": muted_by}},
        upsert=True,
    )


async def remove_gmute(user_id: int):
    await gmute_col.delete_one({"user_id": user_id})


async def is_gmuted(user_id: int) -> bool:
    return bool(await gmute_col.find_one({"user_id": user_id}))


async def get_gmute(user_id: int):
    return await gmute_col.find_one({"user_id": user_id})


async def get_gmute_list():
    return [doc async for doc in gmute_col.find({})]


async def gmute_count() -> int:
    return await gmute_col.count_documents({})
