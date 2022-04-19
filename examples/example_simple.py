import asyncio

import asyncodbc


async def example():
    dsn = "Driver=SQLite;Database=sqlite.db"
    conn = await asyncodbc.connect(
        dsn=dsn,
    )

    cur = await conn.cursor()
    await cur.execute("SELECT 42 AS age;")
    rows = await cur.fetchall()
    print(rows)
    print(rows[0])
    print(rows[0].age)
    await cur.close()
    await conn.close()


if __name__ == "__main__":
    asyncio.run(example())
