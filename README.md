# Playing with libSQL

[libSQL](https://github.com/tursodatabase/libsql) ([Manifesto](https://turso.tech/libsql-manifesto)) by [Turso](https://turso.tech/) is an open-source fork of sqlite. It's super fast, lightweight, and pretty simple to self host.

Turso created a server mode for libSQL called **sqld**. There are a few options for self hosting sqld, but but we will use the precompiled Docker image method on our local machine.

## A Makefile to rule them all

```bash
$ make
vailable make commands:

alive                     Run `sqld -help` on the container 'libsql-server_latest' to check it is alive
first-start               Run a new container 'libsql-server_latest' using the image ghcr.io/tursodatabase/libsql-server
generate-jsw              Run a simple script to generate an ED25519 key pairs and JWT token. Test the last one with and without expiration time.
playing-with-libsql       Run a simple script to test the database
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
$ uv init --script playing-with-libsql.py
Initialized script at `playing-with-libsql.py`
$ uv add --script playing-with-libsql.py asyncio libsql_client
Updated `playing-with-libsql.py`
```

```bash
$ make playing-with-libsql
uv run --script playing-with-libsql.py
1 rows
('It works!!!',)
```

Note that the connection URL is hardcoded as a simplification but best practice is that these values are defined in environment variables. The following scripts suffer from the same simplification.

## Make a backup

Make the backup (WIP)

```bash
$ now=$(date +"%Y%m%d"); sqlite3 sqld-data/iku.db/dbs/default/data '.dump' > /tmp/$now.backup.sql
$ ls /tmp/*.backup.sql
/tmp/20250523.backup.sql
$ cat /tmp/20250523.backup.sql
```

Now, you can restore to another database in the following way

```bash
$ cat /tmp/20250523.backup.sql | sqlite3 a_restructured.sqlite3
```

## Add authentication to secure the db server

### Generate and verify a key pairs and JWT token

Generate a JWT token using the libraries:
- [pyJWT](https://pyjwt.readthedocs.io/en/stable/index.html)is a Python library which allows you to encode and decode JSON Web Tokens (JWT). JWT is an open, industry-standard (RFC 7519) for representing claims securely between two parties.
- [cryptography](https://cryptography.io/en/latest/)is a package designed to expose cryptographic primitives and recipes to Python developers.

```bash
$ uv init --script generate-jsw.py
Initialized script at `generate-jsw.py`
$ uv add --script generate-jsw.py pyJWT cryptography
Updated `generate-jsw.py`
```

```bash
$ make generate-jsw
uv run --script generate-jsw.py
Public Key: b'LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUNvd0JRWURLMlZ3QXlFQXRTYlVyVXNvWForMU5aQzdRNVpYZW9ZSHpTTk5hTmZ4ODR5TkRkNzZxZXc9Ci0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQo='
----- Should get the payload (no expiration time)
JWT: eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoiYWNjZXNzIn0.7OSZSWWDOQDSYPEQrCpbBEjfFU3qmL7X2c2On4HA2C5AOIZqM_VhR6nmbYY-2u6-vDA7E_hODsbPMB35pBwGDg
payload: {'a': 'access'}
----- Should raise an exception when token expire after 2 seconds
JWT: eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoiYWNjZXNzIiwiZXhwIjoxNzQ3OTMyNjkwfQ.DGC7nCWj7xmZKcPeYb7qsoZg8cBxgmdiTuIjk4cFfio5j_78dIR-uT7nfkWj1X2QN9F2jdgViznpNjrz665zCQ
Sleep for 2 seconds
Traceback (most recent call last):
  File "/home/test-libsql/generate-jsw.py", line 94, in <module>
    main()
    ~~~~^^
  File "/home/test-libsql/generate-jsw.py", line 89, in main
    decode = decode_jwt_token(token, public_key_pem)
  File "/home/test-libsql/generate-jsw.py", line 67, in decode_jwt_token
    encoded = jwt.decode(token, secret, algorithms='EdDSA')
  File "/home/test-libsql/.cache/uv/archive-v0/RwwjPIVy3OWC5AYIjmVAA/lib/python3.13/site-packages/jwt/api_jwt.py", line 222, in decode
    decoded = self.decode_complete(
        jwt,
    ...<8 lines>...
        leeway=leeway,
    )
  File "/home/test-libsql/.cache/uv/archive-v0/RwwjPIVy3OWC5AYIjmVAA/lib/python3.13/site-packages/jwt/api_jwt.py", line 167, in decode_complete
    self._validate_claims(
    ~~~~~~~~~~~~~~~~~~~~~^
        payload,
        ^^^^^^^^
    ...<4 lines>...
        subject=subject,
        ^^^^^^^^^^^^^^^^
    )
    ^
  File "/home/test-libsql/.cache/uv/archive-v0/RwwjPIVy3OWC5AYIjmVAA/lib/python3.13/site-packages/jwt/api_jwt.py", line 262, in _validate_claims
    self._validate_exp(payload, now, leeway)
    ~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
  File "/home/test-libsql/.cache/uv/archive-v0/RwwjPIVy3OWC5AYIjmVAA/lib/python3.13/site-packages/jwt/api_jwt.py", line 363, in _validate_exp
    raise ExpiredSignatureError("Signature has expired")
jwt.exceptions.ExpiredSignatureError: Signature has expired
```

---
Related to the articles [SQLite-on-the-Server Is Misunderstood: Better At Hyper-Scale Than Micro-Scale](https://rivet.gg/blog/2025-02-16-sqlite-on-the-server-is-misunderstood) and [Self-hosting Turso libSQL](https://hubertlin.me/posts/2024/11/self-hosting-turso-libsql/)
