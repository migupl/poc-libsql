# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "sqlalchemy",
#     "sqlalchemy-libsql",
# ]
# ///

from sqlalchemy import create_engine, select, Column, Integer, DateTime, MetaData, Table, Text
from sqlalchemy.orm import Session
from sqlalchemy.sql import func


def main(db_url: str) -> None:
    metadata = MetaData()
    users = Table(
        "users",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("username", Text, nullable=False),
        Column("email", Text, nullable=False),
        Column("created_at", DateTime, default=func.now()),
    )

    engine = create_engine(db_url, connect_args={"check_same_thread": False}, echo=True)
    with Session(engine) as session:
        insert_stmt = users.insert().values(username="spongebob", email="spongebob@sqlalchemy.org")
        session.execute(insert_stmt)
        session.commit()

        select_stmt = select(users)
        result = session.execute(select_stmt)
        for row in result:
            print(row)


if __name__ == "__main__":
    main(
        "sqlite+libsql://localhost:8080"
    )
