# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "asyncio",
#     "libsql-client",
# ]
# ///

import asyncio
import libsql_client


async def main(url) -> None:
    async with libsql_client.create_client(url) as client:
        result_set = await client.execute("SELECT 'It works!!!'")
        print(len(result_set.rows), "rows")
        for row in result_set.rows:
            print(row)


if __name__ == "__main__":
    url = 'ws://localhost:8080'
    asyncio.run(main(url))
