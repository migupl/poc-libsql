# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "libsql-experimental",
# ]
# ///

import libsql_experimental as libsql


def main(url: str) -> None:
    conn = libsql.connect("local.db", sync_interval=20, sync_url=url)
    conn.sync()

    print(conn.execute("SELECT * FROM users").fetchall())


if __name__ == "__main__":
    main(
        "http://localhost:8080"
    )
