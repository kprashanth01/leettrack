from app.database import get_database_url


def test_get_database_url_uses_sqlite_fallback_when_env_is_missing(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_DB_HOST", raising=False)
    monkeypatch.delenv("SUPABASE_DB_PASSWORD", raising=False)

    assert get_database_url() == "sqlite:///./leettrack.db"


def test_get_database_url_uses_psycopg_driver_for_supabase_url(monkeypatch) -> None:
    monkeypatch.delenv("SUPABASE_DB_HOST", raising=False)
    monkeypatch.delenv("SUPABASE_DB_PASSWORD", raising=False)
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://postgres:password@db.example.supabase.co:5432/postgres",
    )

    assert (
        get_database_url()
        == "postgresql+psycopg://postgres:password@db.example.supabase.co:5432/postgres"
    )


def test_get_database_url_accepts_legacy_postgres_scheme(monkeypatch) -> None:
    monkeypatch.delenv("SUPABASE_DB_HOST", raising=False)
    monkeypatch.delenv("SUPABASE_DB_PASSWORD", raising=False)
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgres://postgres:password@db.example.supabase.co:5432/postgres",
    )

    assert (
        get_database_url()
        == "postgresql+psycopg://postgres:password@db.example.supabase.co:5432/postgres"
    )


def test_get_database_url_encodes_special_characters_in_database_url(monkeypatch) -> None:
    monkeypatch.delenv("SUPABASE_DB_HOST", raising=False)
    monkeypatch.delenv("SUPABASE_DB_PASSWORD", raising=False)
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://postgres:pass[word]@with:symbols@db.example.supabase.co:5432/postgres",
    )

    assert (
        get_database_url()
        == "postgresql+psycopg://postgres:pass%5Bword%5D%40with%3Asymbols@db.example.supabase.co:5432/postgres"
    )


def test_get_database_url_builds_url_from_supabase_components(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SUPABASE_DB_HOST", "db.example.supabase.co")
    monkeypatch.setenv("SUPABASE_DB_PORT", "5432")
    monkeypatch.setenv("SUPABASE_DB_NAME", "postgres")
    monkeypatch.setenv("SUPABASE_DB_USER", "postgres")
    monkeypatch.setenv("SUPABASE_DB_PASSWORD", "pass[word]@with:symbols")

    assert (
        get_database_url()
        == "postgresql+psycopg://postgres:pass%5Bword%5D%40with%3Asymbols@db.example.supabase.co:5432/postgres"
    )
