import asyncio

import asyncodbc


async def pool():
    dsn = "Driver=SQLite;Database=sqlite.db"
    pool = await asyncodbc.create_pool(dsn=dsn)

    async with pool.acquire() as conn:
        cur = await conn.cursor()
        await cur.execute("SELECT 42;")
        r = await cur.fetchall()
        print(r)
        await cur.close()
        await conn.close()
    pool.close()
    await pool.wait_closed()


if __name__ == "__main__":
    asyncio.run(pool())
