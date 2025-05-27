# Playing with libSQL

[libSQL](https://github.com/tursodatabase/libsql) ([Manifesto](https://turso.tech/libsql-manifesto)) by [Turso](https://turso.tech/) is an open-source fork of sqlite. It's super fast, lightweight, and pretty simple to self host.

Turso created a server mode for libSQL called **sqld**. There are a few options for self hosting sqld, but but we will use the precompiled Docker image method on our local machine.

## A Makefile to rule them all

```bash
$ make
Available make commands:

alive                     Run `sqld -help` on the container 'libsql-server_latest' to check it is alive
embedded-replicas         Run a simple script to test the embedded database.
first-start               Run a new container 'libsql-server_latest' using the image ghcr.io/tursodatabase/libsql-server
generate-jwt              Run a simple script to generate an ED25519 key pairs and JWT token. Test the last one with and without expiration time.
playing-with-libsql       Run a simple script to test the database. When JWT_TOKEN variable exists then the secure server is used.
start                     Run the container 'libsql-server_latest'
stop                      Stop the container 'libsql-server_latest'
```

## Run `sqld` using Docker

Data are persisted at the folder `./sqld-data`

Run for the first time

```bash
$ make first-start
mkdir -p sqld-dat
docker run -p 8080:8080 --name libsql-server_latest -v `pwd`/sqld-data:/var/lib/sqld -d ghcr.io/tursodatabase/libsql-server:latest
431a33576a14bfb09e0fa1a4133c94d2ec78ffc66058e2a3fa0b5c188f565a0b
$
```

```bash
$ tree sqld-data
sqld-data
└── iku.db
    ├── dbs
    │   └── default
    │       ├── data
    │       ├── data-shm
    │       ├── data-wal
    │       ├── stats.json
    │       ├── tmp
    │       ├── to_compact
    │       └── wallog
    └── metastore
        ├── data
        ├── data-shm
        └── data-wal

7 directories, 8 files
```

After stopping the container

```bash
$ make stop
docker stop libsql-server_latest
libsql-server_latest
```

the following executions will be performed with

```bash
$ make start
docker start libsql-server_latest
libsql-server_latest
```

The service exposes the database at URL `ws://localhost:8080`.

## Test the container is running

```bash
$ docker ps
CONTAINER ID   IMAGE                                        COMMAND                  CREATED         STATUS                             PORTS                              NAMES
eebbb0f9c471   ghcr.io/tursodatabase/libsql-server:latest   "/usr/local/bin/dock…"   2 hours ago   Up 33 seconds   5001/tcp, 0.0.0.0:8080->8080/tcp   libsql-server_latest
```

Execute `sqld --help` into container

```bash
$ make alive
docker exec -it libsql-server_latest /bin/sqld --help
SQL daemon

Usage: sqld [OPTIONS] [COMMAND]

Commands:
  admin-shell
  help         Print this message or the help of the given subcommand(s)

Options:
  -d, --db-path <DB_PATH>
          [env: SQLD_DB_PATH=]
          [default: data.sqld]
...
```

## Run a simple script

Python tool [uv](https://docs.astral.sh/uv/) and its ability to execute single-file Python scripts containing references to external Python packages without much ceremony will be used. This feat is achieved by uv with the help of [PEP 723](https://peps.python.org/pep-0723/) which focuses on ‘Inline script metadata’. This PEP defines a standardised method for embedding script metadata, including external package dependencies, directly into single-file Python scripts.

There are two libraries for LibSQL to interact with Python, the [libsql-client](https://github.com/tursodatabase/libsql-client-py) and the [libsql-experimental-python](https://github.com/tursodatabase/libsql-experimental-python). The former is the recommended client as it is stable, whereas the latter is in development and has the latest features from the libsql database engine, however, it is compatible with the [sqlite](https://docs.python.org/3/library/sqlite3.html) module.

```bash
$ uv init --script ./scripts/playing-with-libsql.py
Initialized script at `script/playing-with-libsql.py`
$ uv add --script ./scripts/playing-with-libsql.py argparse asyncio libsql_client
Updated `script/playing-with-libsql.py`
```

```bash
$ make playing-with-libsql
uv run --script playing-with-libsql.py
1 rows
('It works!!!',)
```

Note that the connection URL is hardcoded as a simplification but best practice is that these values are defined in environment variables. The following scripts suffer from the same simplification.

## Browse the data

There are some [supported GUIs](https://github.com/tursodatabase/libsql?tab=readme-ov-file#gui-support) such as the [downloaded version](https://github.com/outerbase/studio-desktop/releases/) of [Outerbase Studio Desktop](https://github.com/outerbase/studio) as shown below.

![Outerbase Studio Desktop](./docs/outerbase-studio-desktop.png)

## Add authentication to secure the db server

### Generate and verify a key pairs and JWT token

Generate a JWT token using the libraries:
- [pyJWT](https://pyjwt.readthedocs.io/en/stable/index.html)is a Python library which allows you to encode and decode JSON Web Tokens (JWT). JWT is an open, industry-standard (RFC 7519) for representing claims securely between two parties.
- [cryptography](https://cryptography.io/en/latest/)is a package designed to expose cryptographic primitives and recipes to Python developers.

Create the new script

```bash
$ uv init --script ./scripts/generate-jwt.py
Initialized script at `script/generate-jwt.py`
$ uv add --script ./scripts/generate-jwt.py pyJWT cryptography
Updated `script/generate-jwt.py`
```

The execution of the script generates the `public.pub` file with the public key in the main directory of the repository as well as a test of the generated tokens.

```bash
$ make generate-jwt
uv run --script ./script/generate-jwt.py
Public Key (bytes):      b'eTfSJ-Qnq_aO6Jg0lGjMo334riU9FPrrNdp_NK--Kj4='

 ----- Should get the payload (no expiration time)
JWT: eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhY2Nlc3MifQ.X0SsKKjTd0rwZ7-PVPS8-2qR7wS0etnBeVSBniWNZlL6MTNY13-QMaq5QyDH7ax5CTioNpVhkDfzKcaP1ad8Cw
payload: {'sub': 'access'}

 ----- Should raise an exception when token expire after 2 seconds
JWT: eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhY2Nlc3MiLCJleHAiOjE3NDgwMTIxMzZ9.3Zwgym6mWJ8U9ZWWXeaTUrKKZDJhc20b3EYVYooYnvvRsH0Tzmp2loph-0NpYrEcM8QiSIlixrZ0Pej1kd9tAA
Sleep for 2 seconds
Traceback (most recent call last):
  File "/home/test-libsql/generate-jwt.py", line 94, in <module>
    main()
    ~~~~^^
  File "/home/test-libsql/generate-jwt.py", line 89, in main
    decode = decode_jwt_token(token, public_key_pem)
  File "/home/test-libsql/generate-jwt.py", line 67, in decode_jwt_token
    encoded = jwt.decode(token, secret, algorithms='EdDSA')
  File "/home/test-libsql/.cache/uv/archive-v0/hMO5koCWsFhqoXVCM0nkZ/lib/python3.13/site-packages/jwt/api_jwt.py", line 222, in decode
    decoded = self.decode_complete(
        jwt,
    ...<8 lines>...
        leeway=leeway,
    )
  File "/home/test-libsql/.cache/uv/archive-v0/hMO5koCWsFhqoXVCM0nkZ/lib/python3.13/site-packages/jwt/api_jwt.py", line 167, in decode_complete
    self._validate_claims(
    ~~~~~~~~~~~~~~~~~~~~~^
        payload,
        ^^^^^^^^
    ...<4 lines>...
        subject=subject,
        ^^^^^^^^^^^^^^^^
    )
    ^
  File "/home/test-libsql/.cache/uv/archive-v0/hMO5koCWsFhqoXVCM0nkZ/lib/python3.13/site-packages/jwt/api_jwt.py", line 262, in _validate_claims
    self._validate_exp(payload, now, leeway)
    ~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "/home/test-libsql/.cache/uv/archive-v0/hMO5koCWsFhqoXVCM0nkZ/lib/python3.13/site-packages/jwt/api_jwt.py", line 363, in _validate_exp
    raise ExpiredSignatureError("Signature has expired")
jwt.exceptions.ExpiredSignatureError: Signature has expired
```

### Securize the server

To secure the server, set the file name with the public key in the server environment variable `SQLD_AUTH_JWT_KEY_FILE` ([libSQL daemon .env-example](https://gist.github.com/darkterminal/8b9503b95f35b691a74dd73394675b3a))

```bash
$ cat .env
# JWT Key File for Authentication
SQLD_AUTH_JWT_KEY_FILE=public.pub
```

If we copy the previously generated file `public.pub` to the data directory `sqld-data`

```bash
$ cp public.pub sqld-data/.
```

then the server will be secured.

Create the securized server the fisrt time as following

```bash
$ make first-start
mkdir -p sqld-data
docker run -p 8080:8080 --name secure-libsql-server_latest --env-file .env -v `pwd`/sqld-data:/var/lib/sqld -d ghcr.io/tursodatabase/libsql-server:latest
d498ad894c974efda905b225ccedb20d441ca58ce5769b3879183fe8cdbf8764
```

Note that the name of the container changes to `secure-libsql-server_latest` and the file `.env` is passed to the container.

The following times we will use

```bash
$ make start
docker start secure-libsql-server_latest
secure-libsql-server_latest
```

Running the existing script `playing-with-libsql.py` without arguments should end in the error
*Authentication failed: Expected authorization header but none given*

```bash
$ make playing-with-libsql
uv run --script ./script/playing-with-libsql.py
Traceback (most recent call last):
  File "/home/test-libsql/playing-with-libsql.py", line 28, in <module>
    asyncio.run(main(url))
    ~~~~~~~~~~~^^^^^^^^^^^
  File "/usr/lib/python3.13/asyncio/runners.py", line 195, in run
    return runner.run(main)
           ~~~~~~~~~~^^^^^^
  File "/usr/lib/python3.13/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/usr/lib/python3.13/asyncio/base_events.py", line 719, in run_until_complete
    return future.result()
           ~~~~~~~~~~~~~^^
  File "/home/test-libsql/playing-with-libsql.py", line 15, in main
    await client.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER);")
  File "/home/test-libsql/.cache/uv/archive-v0/_vDrrszsZqtMBJrr-feY9/lib/python3.13/site-packages/libsql_client/hrana/client.py", line 75, in execute
    return _result_set_from_proto(await proto_result_fut)
                                  ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/test-libsql/.cache/uv/archive-v0/_vDrrszsZqtMBJrr-feY9/lib/python3.13/site-packages/libsql_client/hrana/conn.py", line 118, in _do_receive
    self._receive(msg.data)
    ~~~~~~~~~~~~~^^^^^^^^^^
  File "/home/test-libsql/.cache/uv/archive-v0/_vDrrszsZqtMBJrr-feY9/lib/python3.13/site-packages/libsql_client/hrana/conn.py", line 235, in _receive
    raise _error_from_proto(msg["error"])
libsql_client.client.LibsqlError: AUTH_HEADER_NOT_FOUND: Authentication failed: Expected authorization header but none given
```

Running the existing script `playing-with-libsql.py` but using the generated JWT token before

```bash
$ make playing-with-libsql JWT_TOKEN="eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhY2Nlc3MifQ.X0SsKKjTd0rwZ7-PVPS8-2qR7wS0etnBeVSBniWNZlL6MTNY13-QMaq5QyDH7ax5CTioNpVhkDfzKcaP1ad8Cw"
uv run --script playing-with-libsql.py eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhY2Nlc3MifQ.X0SsKKjTd0rwZ7-PVPS8-2qR7wS0etnBeVSBniWNZlL6MTNY13-QMaq5QyDH7ax5CTioNpVhkDfzKcaP1ad8Cw
1 rows
(99,)
```

and using the expired JWT token must end in the error *Authentication failed: The JWT has expired*

```bash
$ make playing-with-libsql JWT_TOKEN="eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhY2Nlc3MiLCJleHAiOjE3NDgwMTIxMzZ9.3Zwgym6mWJ8U9ZWWXeaTUrKKZDJhc20b3EYVYooYnvvRsH0Tzmp2loph-0NpYrEcM8QiSIlixrZ0Pej1kd9tAA"
uv run --script ./script/playing-with-libsql.py eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhY2Nlc3MiLCJleHAiOjE3NDgwMTIxMzZ9.3Zwgym6mWJ8U9ZWWXeaTUrKKZDJhc20b3EYVYooYnvvRsH0Tzmp2loph-0NpYrEcM8QiSIlixrZ0Pej1kd9tAA
Traceback (most recent call last):
  File "/home/test-libsql/playing-with-libsql.py", line 36, in <module>
    asyncio.run(
    ~~~~~~~~~~~^
        main('ws://localhost:8080', args.jwt_token)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/usr/lib/python3.13/asyncio/runners.py", line 195, in run
    return runner.run(main)
           ~~~~~~~~~~^^^^^^
  File "/usr/lib/python3.13/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/usr/lib/python3.13/asyncio/base_events.py", line 719, in run_until_complete
    return future.result()
           ~~~~~~~~~~~~~^^
  File "/home/test-libsql/playing-with-libsql.py", line 19, in main
    await client.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER);")
  File "/home/test-libsql/.cache/uv/archive-v0/Vavx-WJM0p91f9a24E9QA/lib/python3.13/site-packages/libsql_client/hrana/client.py", line 75, in execute
    return _result_set_from_proto(await proto_result_fut)
                                  ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/test-libsql/.cache/uv/archive-v0/Vavx-WJM0p91f9a24E9QA/lib/python3.13/site-packages/libsql_client/hrana/conn.py", line 118, in _do_receive
    self._receive(msg.data)
    ~~~~~~~~~~~~~^^^^^^^^^^
  File "/home/test-libsql/.cache/uv/archive-v0/Vavx-WJM0p91f9a24E9QA/lib/python3.13/site-packages/libsql_client/hrana/conn.py", line 235, in _receive
    raise _error_from_proto(msg["error"])
libsql_client.client.LibsqlError: AUTH_JWT_EXPIRED: Authentication failed: The JWT has expired
```

## Migrations

Database migrations serve as a standard procedure for managing and tracking changes in the schema of application databases over time. This method ensures that changes are systematically recorded.

Following the article [Database migrations with Geni and libSQL](https://turso.tech/blog/database-migrations-with-geni) we will use [Geni](https://github.com/emilpriver/geni) for a small test.

A `migrations` directory is created for the management of migrations.

Let's create a migration

```bash
$ docker run --rm -it --network=host -v `pwd`/migrations:/migrations ghcr.io/emilpriver/geni:latest new create_users_table
11:35:06 [INFO] Generated /migrations/1748259306_create_users_table.up.sql
11:35:06 [INFO] Generated /migrations/1748259306_create_users_table.down.sql
11:35:06 [INFO] Success
```

Both files are modified as shown below

```bash
$ cat migrations/1748259306_create_users_table.up.sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  email TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
$ cat migrations/1748259306_create_users_table.down.sql
DROP TABLE users;
```

Obviously there is a pending migration

```bash
$ docker run --rm -it --network=host -e DATABASE_URL='http://localhost:8080' -v `pwd`/migrations:/migrations ghcr.io/emilpriver/geni:latest status
12:25:37 [INFO] Token is not set, using empty string
12:25:37 [INFO] Pending 1748259306
```

Apply a first migration

```bash
$ docker run --rm -it --network=host -e DATABASE_URL='http://localhost:8080' -v `pwd`/migrations:/migrations ghcr.io/emilpriver/geni:latest up
11:53:29 [INFO] Token is not set, using empty string
11:53:29 [INFO] Running migration 1748259306
11:53:29 [INFO] Success
```

*Geni* automatically generates the following LibSQL SQL Schema dump as follows

```bash
$ cat migrations/schema.sql
--
-- LibSQL SQL Schema dump automatic generated by geni
--

CREATE TABLE schema_migrations (id VARCHAR(255) NOT NULL PRIMARY KEY);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  email TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

![Table 'User'](./docs/migrations_up.png)

The mentioned article contains more interesting information such as [the automation of migrations](https://turso.tech/blog/database-migrations-with-geni#automating-migrations).

## Make a backup

Make the backup

```bash
$ now=$(date +"%Y%m%d"); sqlite3 sqld-data/iku.db/dbs/default/data '.dump' > /tmp/$now.backup.sql
$ ls /tmp/*.backup.sql
/tmp/20250526.backup.sql
```

```bash
$ cat /tmp/20250526.backup.sql
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE schema_migrations (id VARCHAR(255) NOT NULL PRIMARY KEY);
INSERT INTO schema_migrations VALUES('1748259306');
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  email TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
COMMIT;
```

Now, you can restore to another database in the following way

```bash
$ cat /tmp/20250526.backup.sql | sqlite3 a_restructured.sqlite3
```

## Insert an user after the first migration using [SQLAlchemy](https://docs.sqlalchemy.org/en/20/)

A new python script is used

```bash
$ uv init --script ./scripts/insert-using-sqlalchemy.py
Initialized script at `script/insert-using-sqlalchemy.py`
$ uv add --script ./scripts/insert-using-sqlalchemy.py sqlalchemy sqlalchemy-libsql
Updated `script/insert-using-sqlalchemy.py`
```

Run an insert ad following

```bash
$ make start
docker start libsql-server_latest
libsql-server_latest
$ make insert-using-sqlalchemy
uv run --script ./scripts/insert-using-sqlalchemy.py
2025-05-27 14:05:51,315 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-05-27 14:05:51,316 INFO sqlalchemy.engine.Engine INSERT INTO users (username, email, created_at) VALUES (?, ?, CURRENT_TIMESTAMP)
2025-05-27 14:05:51,316 INFO sqlalchemy.engine.Engine [generated in 0.00025s] ('spongebob', 'spongebob@sqlalchemy.org')
2025-05-27 14:05:51,320 INFO sqlalchemy.engine.Engine COMMIT
2025-05-27 14:05:51,324 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-05-27 14:05:51,326 INFO sqlalchemy.engine.Engine SELECT users.id, users.username, users.email, users.created_at
FROM users
2025-05-27 14:05:51,326 INFO sqlalchemy.engine.Engine [generated in 0.00024s] ()
(1, 'spongebob', 'spongebob@sqlalchemy.org', datetime.datetime(2025, 5, 27, 12, 5, 51))
2025-05-27 14:05:51,328 INFO sqlalchemy.engine.Engine ROLLBACK
```

## Local First, embedded Replicas

Embedded replicas provide a smooth switch between local and remote database operations, allowing the same database to adapt to various scenarios effortlessly. They also ensure speedy data access by syncing local copies with the remote database, enabling microsecond-level read operations — a significant advantage for scenarios demanding quick data retrieval.

### Offline Reads

A new script `embedded-replicas.py` is used

```bash
$ uv init --script ./scripts/embedded-replicas.py
Initialized script at `script/embedded-replicas.py`
$ uv add --script ./scripts/embedded-replicas.py libsql-experimental
Updated `script/embedded-replicas.py`
```

Start the server

```bash
$ make start
docker start libsql-server_latest
libsql-server_latest
```

Create the embedded replica `local.db` with the first execution

```bash
$ make embedded-replicas
uv run --script ./scripts/embedded-replicas.py
2025-05-27T15:33:39.647616Z  INFO libsql::replication::remote_client: Attempting to perform handshake with primary.
[]
```

The local files created

```bash
$ ls -1 local.*
local.db
local.db-client_wal_index
```

Insert an user into the database

```bash
$ make insert-using-sqlalchemy
uv run --script ./scripts/insert-using-sqlalchemy.py
2025-05-27 17:35:22,682 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-05-27 17:35:22,684 INFO sqlalchemy.engine.Engine INSERT INTO users (username, email, created_at) VALUES (?, ?, CURRENT_TIMESTAMP)
2025-05-27 17:35:22,684 INFO sqlalchemy.engine.Engine [generated in 0.00025s] ('spongebob', 'spongebob@sqlalchemy.org')
2025-05-27 17:35:22,688 INFO sqlalchemy.engine.Engine COMMIT
2025-05-27 17:35:22,692 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-05-27 17:35:22,693 INFO sqlalchemy.engine.Engine SELECT users.id, users.username, users.email, users.created_at 
FROM users
2025-05-27 17:35:22,693 INFO sqlalchemy.engine.Engine [generated in 0.00020s] ()
(1, 'spongebob', 'spongebob@sqlalchemy.org', datetime.datetime(2025, 5, 27, 15, 35, 22))
2025-05-27 17:35:22,696 INFO sqlalchemy.engine.Engine ROLLBACK
```

Sync the embedded replica

```bash
$ make embedded-replicas
uv run --script ./scripts/embedded-replicas.py
2025-05-27T15:35:58.983279Z  INFO libsql::replication::remote_client: Attempting to perform handshake with primary.
[(1, 'spongebob', 'spongebob@sqlalchemy.org', '2025-05-27 15:35:22')]
```

and the `local.db` dump shows the synchronized data

```bash
$ sqlite3 local.db .dump
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE schema_migrations (id VARCHAR(255) NOT NULL PRIMARY KEY);
INSERT INTO schema_migrations VALUES('1748259306');
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  email TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO users VALUES(1,'spongebob','spongebob@sqlalchemy.org','2025-05-27 15:17:30');
INSERT INTO sqlite_sequence VALUES('users',1);
COMMIT;
```

The script is running an explicit synchronisation

```python
conn = libsql.connect("local.db", sync_url=url)
conn.sync()
...
```

A periodic synchronisation could be used as following

```python
conn = libsql.connect("local.db", sync_interval=20, sync_url=url)
...
```

### Offline Writes

Write locally, even offline, and let Turso manage the sync to and from your remote database.

Currently, May 2025, in beta testing.

## Database encryption

libSQL allows [encryption at rest](https://docs.turso.tech/features/embedded-replicas/introduction#encryption-at-rest). This feature enhances data security by encrypting database files, making them inaccessible without the correct encryption key.

Encrypted databases appear as raw data and cannot be read as standard SQLite databases. You must use the [libSQL client for any operations](https://docs.turso.tech/features/embedded-replicas/introduction#encryption-at-rest).


## Run without install `uv` using Docker

Setting an alias and executing the examples without using make is an easy way to go

```bash
$ alias uv='docker run --rm -it --network="host" --volume .:/app ghcr.io/astral-sh/uv:alpine uv'
$ uv run --script /app/scripts/playing-with-libsql.py
Installed 35 packages in 54ms

1 rows
('It works!!!',)
```

---
Inspired by articles [SQLite-on-the-Server Is Misunderstood: Better At Hyper-Scale Than Micro-Scale](https://rivet.gg/blog/2025-02-16-sqlite-on-the-server-is-misunderstood) and [Self-hosting Turso libSQL](https://hubertlin.me/posts/2024/11/self-hosting-turso-libsql/)
