# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "argparse",
#     "asyncio",
#     "libsql-client",
# ]
# ///

from argparse import ArgumentParser

import asyncio
import libsql_client


async def get_client(url: str, jwt_token: str):
    if jwt_token:
        return libsql_client.create_client(url, auth_token=jwt_token)

    return libsql_client.create_client(url)


async def main(libsql_client) -> None:
    async with await libsql_client as client:
        result_set = await client.execute("SELECT 'It works!!!'")
        print(len(result_set.rows), "rows")
        for row in result_set.rows:
            print(row)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("jwt_token", help="JWT token used in the request (JWT_TOKEN)", nargs='?', default='')
    args = parser.parse_args()

    asyncio.run(main(
        get_client('ws://localhost:8080', args.jwt_token)
    ))
