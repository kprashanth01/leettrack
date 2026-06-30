import os
from collections.abc import Generator
from urllib.parse import parse_qsl

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()


def get_database_url() -> str:
    component_url = get_component_database_url()
    if component_url is not None:
        return component_url

    database_url = os.getenv("DATABASE_URL", "sqlite:///./leettrack.db")
    if database_url.startswith("postgres://"):
        return normalize_postgres_database_url(database_url)
    if database_url.startswith("postgresql://"):
        return normalize_postgres_database_url(database_url)
    return database_url


def normalize_postgres_database_url(database_url: str) -> str:
    raw_url = database_url.replace("postgres://", "postgresql://", 1)
    _, rest = raw_url.split("://", 1)

    credentials, host_path = rest.rsplit("@", 1)
    username, password = credentials.split(":", 1)
    host_port, path_query = host_path.split("/", 1)

    if ":" in host_port:
        host, raw_port = host_port.rsplit(":", 1)
        port = int(raw_port)
    else:
        host = host_port
        port = 5432

    if "?" in path_query:
        database, raw_query = path_query.split("?", 1)
        query = dict(parse_qsl(raw_query))
    else:
        database = path_query
        query = {}

    return URL.create(
        drivername="postgresql+psycopg",
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
        query=query,
    ).render_as_string(hide_password=False)


def get_component_database_url() -> str | None:
    host = os.getenv("SUPABASE_DB_HOST")
    password = os.getenv("SUPABASE_DB_PASSWORD")
    user = os.getenv("SUPABASE_DB_USER", "postgres")
    database = os.getenv("SUPABASE_DB_NAME", "postgres")
    port = int(os.getenv("SUPABASE_DB_PORT", "5432"))

    if not host or not password:
        return None

    return URL.create(
        drivername="postgresql+psycopg",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database,
    ).render_as_string(hide_password=False)


def create_database_engine(database_url: str | None = None) -> Engine:
    url = database_url or get_database_url()
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)


engine = create_database_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
