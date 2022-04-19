import asyncio

import asyncodbc


async def example():
    dsn = "Driver=SQLite;Database=sqlite.db"

    async with asyncodbc.create_pool(dsn=dsn) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 42 AS age;")
                val = await cur.fetchone()
                print(val)
                print(val.age)


if __name__ == "__main__":
    asyncio.run(example())
