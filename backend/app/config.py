import os


DEFAULT_CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
    "http://localhost:5176",
    "http://127.0.0.1:5176",
]


class RuntimeConfigurationError(RuntimeError):
    pass


def get_app_environment() -> str:
    return os.getenv("APP_ENV") or os.getenv("ENVIRONMENT") or "local"


def get_cors_allowed_origins() -> list[str]:
    configured_origins = os.getenv("CORS_ALLOWED_ORIGINS")
    if not configured_origins:
        return DEFAULT_CORS_ALLOWED_ORIGINS

    return [
        origin.strip()
        for origin in configured_origins.split(",")
        if origin.strip()
    ]


def validate_runtime_configuration() -> None:
    if get_app_environment().lower() not in {"production", "prod"}:
        return

    missing = _missing_production_configuration()
    if missing:
        raise RuntimeConfigurationError(
            "Missing production configuration: " + ", ".join(missing)
        )


def _missing_production_configuration() -> list[str]:
    required_keys = [
        "SUPABASE_URL",
        "SUPABASE_PUBLISHABLE_KEY",
        "RESEND_API_KEY",
        "EMAIL_FROM",
        "SCHEDULER_SECRET",
        "CORS_ALLOWED_ORIGINS",
    ]
    missing = [key for key in required_keys if not os.getenv(key)]

    if not _has_database_configuration():
        missing.insert(0, "DATABASE_URL or SUPABASE_DB_HOST/SUPABASE_DB_PASSWORD")

    return missing


def _has_database_configuration() -> bool:
    if os.getenv("DATABASE_URL"):
        return True

    return bool(os.getenv("SUPABASE_DB_HOST") and os.getenv("SUPABASE_DB_PASSWORD"))
