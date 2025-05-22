# Playing with libSQL

[libSQL](https://github.com/tursodatabase/libsql) ([Manifesto](https://turso.tech/libsql-manifesto)) by [Turso](https://turso.tech/) is an open-source fork of sqlite. It's super fast, lightweight, and pretty simple to self host.

Turso created a server mode for libSQL called sqld which we'll be using on a VPS (Virtual Private Server).

There are a few options for self hosting sqld, but I'll be using the prebuilt Docker image method.

## Run `sqld` using Docker

Data are persisted at the folder `./sqld-data`

Run for the first time

```bash
$ docker run -p 8080:8080 --name libsql-server_latest -v `pwd`/sqld-data:/var/lib/sqld -d ghcr.io/tursodatabase/libsql-server:latest
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

After stopping the container, the following executions will be performed with

```bash
$ docker start  libsql-server_latest
libsql-server_latest
```

## Test the container is running

```bash
$ docker ps
CONTAINER ID   IMAGE                                        COMMAND                  CREATED         STATUS                             PORTS                              NAMES
23e688261db8   ghcr.io/tursodatabase/libsql-server:latest   "/usr/local/bin/dock…"   7 seconds ago   Up 6 seconds                       5001/tcp, 0.0.0.0:8080->8080/tcp   suspicious_taussig
```

Execute `sqld --help` into container

```bash
$ docker exec -it ghcr.io/tursodatabase/libsql-server:latest /bin/sqld --help
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

---
Related to the articles [SQLite-on-the-Server Is Misunderstood: Better At Hyper-Scale Than Micro-Scale](https://rivet.gg/blog/2025-02-16-sqlite-on-the-server-is-misunderstood) and [Self-hosting Turso libSQL](https://hubertlin.me/posts/2024/11/self-hosting-turso-libsql/)
