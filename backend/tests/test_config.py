import pytest

from app.config import (
    RuntimeConfigurationError,
    get_cors_allowed_origins,
    validate_runtime_configuration,
)


def test_get_cors_allowed_origins_uses_local_defaults(monkeypatch) -> None:
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)

    assert "http://localhost:5173" in get_cors_allowed_origins()
    assert "http://127.0.0.1:5173" in get_cors_allowed_origins()


def test_get_cors_allowed_origins_trims_empty_values(monkeypatch) -> None:
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS",
        " https://leettrack.vercel.app, ,http://localhost:5173 ",
    )

    assert get_cors_allowed_origins() == [
        "https://leettrack.vercel.app",
        "http://localhost:5173",
    ]


def test_validate_runtime_configuration_allows_local_defaults(monkeypatch) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("ENVIRONMENT", raising=False)

    validate_runtime_configuration()


def test_validate_runtime_configuration_requires_production_secrets(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    for key in [
        "DATABASE_URL",
        "SUPABASE_DB_HOST",
        "SUPABASE_DB_PASSWORD",
        "SUPABASE_URL",
        "SUPABASE_PUBLISHABLE_KEY",
        "RESEND_API_KEY",
        "EMAIL_FROM",
        "SCHEDULER_SECRET",
        "CORS_ALLOWED_ORIGINS",
    ]:
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(RuntimeConfigurationError) as exc:
        validate_runtime_configuration()

    assert "SUPABASE_URL" in str(exc.value)
    assert "DATABASE_URL or SUPABASE_DB_HOST/SUPABASE_DB_PASSWORD" in str(exc.value)


def test_validate_runtime_configuration_accepts_component_database_config(
    monkeypatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SUPABASE_DB_HOST", "aws-0-us-east-1.pooler.supabase.com")
    monkeypatch.setenv("SUPABASE_DB_PASSWORD", "secret")
    monkeypatch.setenv("SUPABASE_URL", "https://project.supabase.co")
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "publishable")
    monkeypatch.setenv("RESEND_API_KEY", "re_secret")
    monkeypatch.setenv("EMAIL_FROM", "LeetTrack <hello@example.com>")
    monkeypatch.setenv("SCHEDULER_SECRET", "scheduler-secret")
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://leettrack.vercel.app")

    validate_runtime_configuration()
