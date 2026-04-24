# src/docuview/core/config.py
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import Field, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

# ---------------------------------------------------------------------------
# Пути к конфигурации
# ---------------------------------------------------------------------------


def _config_dir() -> Path:
    """
    Каталог с config.yaml и secrets.env.
    Переопределяется через DOCUVIEW_CONFIG_DIR, по умолчанию ~/.config/docuview.
    """
    return Path(
        os.environ.get("DOCUVIEW_CONFIG_DIR", Path.home() / ".config" / "docuview")
    ).expanduser()


def _yaml_config_path() -> Path:
    return _config_dir() / "config.yaml"


def _secrets_env_path() -> Path:
    return _config_dir() / "secrets.env"


def _repo_env_path() -> Path:
    # .env в корне репо — оставляем для dev-обратной совместимости
    return Path(".env")


# ---------------------------------------------------------------------------
# YAML source для pydantic-settings
# ---------------------------------------------------------------------------


class YamlConfigSource(PydanticBaseSettingsSource):
    """
    Источник настроек из ~/.config/docuview/config.yaml.
    Плоский маппинг: вложенные секции YAML раскрываются в префиксные поля.
    Например: paths.inbox  ->  paths_inbox
              database.host -> postgres_host (через маппинг ниже)
    """

    # Маппинг YAML-путей -> имена полей Settings.
    # Если ключа нет в маппинге, используется соединение через "_".
    _KEY_MAP: dict[str, str] = {
        # database.* -> postgres_*
        "database.host": "postgres_host",
        "database.port": "postgres_port",
        "database.name": "postgres_db",
        "database.user": "postgres_user",
        # paths.* остаются paths_*
        # etl.* остаются etl_*
        # embeddings.* остаются embeddings_*
        # claude.* остаются claude_*
        # logging.* остаются logging_*
    }

    def __init__(self, settings_cls: type[BaseSettings]) -> None:
        super().__init__(settings_cls)
        self._data = self._load()

    def _load(self) -> dict[str, Any]:
        path = _yaml_config_path()
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        return self._flatten(raw)

    def _flatten(self, data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
        flat: dict[str, Any] = {}
        for key, value in data.items():
            full = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                flat.update(self._flatten(value, full))
            else:
                field_name = self._KEY_MAP.get(full, full.replace(".", "_"))
                # Раскрываем ~ в путях
                if isinstance(value, str) and value.startswith("~"):
                    value = str(Path(value).expanduser())
                flat[field_name] = value
        return flat

    def get_field_value(self, field: Any, field_name: str) -> tuple[Any, str, bool]:
        value = self._data.get(field_name)
        return value, field_name, False

    def __call__(self) -> dict[str, Any]:
        return {k: v for k, v in self._data.items() if v is not None}


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


class Settings(BaseSettings):
    """
    Приоритет источников (от высокого к низкому):
      1. init_kwargs (Settings(foo=...))
      2. переменные окружения
      3. secrets.env  из ~/.config/docuview/
      4. .env         из корня репо (dev-обратная совместимость)
      5. config.yaml  из ~/.config/docuview/
      6. значения по умолчанию в коде
    """

    model_config = SettingsConfigDict(
        # secrets.env имеет приоритет — указан первым
        env_file=(str(_secrets_env_path()), str(_repo_env_path())),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------ App
    app_name: str = "DocuView"
    environment: Literal["local", "dev", "staging", "prod"] = "local"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # ------------------------------------------------------------- Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "docuview"
    postgres_password: str = Field(default=..., repr=False)  # обязателен, не логируем
    postgres_db: str = "docuview"

    # Готовый URL, опционально перекрывает компоненты
    database_url_override: str | None = None

    # ---------------------------------------------------------------- Paths
    # Всё, что читается из paths.* в config.yaml
    paths_work_dir: Path = Path.home() / "docuview"
    paths_inbox: Path = Path.home() / "docuview" / "inbox"
    paths_corpus: Path = Path.home() / "docuview" / "corpus"
    paths_ocr_cache: Path = Path.home() / "docuview" / "ocr-cache"
    paths_uploads_staging: Path = Path.home() / "docuview" / "uploads-staging"
    paths_logs: Path = Path.home() / "docuview" / "logs"
    paths_backup: Path = Path.home() / "docuview" / "backup"

    # ------------------------------------------------------------------ ETL
    etl_parse_workers: int = 2
    etl_ocr_workers: int = 2
    etl_ner_workers: int = 2
    etl_embedding_batch_size: int = 32

    # ----------------------------------------------------------- Embeddings
    embeddings_model: str = "intfloat/multilingual-e5-small"
    embeddings_device: Literal["cpu", "cuda", "mps"] = "cpu"

    # --------------------------------------------------------------- Claude
    claude_model: str = "claude-sonnet-4-5"
    claude_fallback_model: str = "claude-haiku-4-5"
    claude_daily_budget_usd: float = 5.0
    claude_prompt_caching: bool = True
    anthropic_api_key: str | None = Field(default=None, repr=False)

    # -------------------------------------------------------------- Logging
    logging_file: Path | None = None
    logging_max_bytes: int = 10 * 1024 * 1024
    logging_backup_count: int = 5

    # ============================================================ Computed

    @computed_field  # type: ignore[misc]
    @property
    def database_url(self) -> str:
        """Async URL для SQLAlchemy/asyncpg."""
        if self.database_url_override:
            return self.database_url_override
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                path=self.postgres_db,
            )
        )

    @computed_field  # type: ignore[misc]
    @property
    def database_url_sync(self) -> str:
        """Sync URL (psycopg) — для Alembic offline или скриптов."""
        return self.database_url.replace("postgresql+asyncpg", "postgresql+psycopg")

    @computed_field  # type: ignore[misc]
    @property
    def config_dir(self) -> Path:
        return _config_dir()

    # =========================================================== Sources

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Порядок = приоритет (первый источник важнее).
        YAML кладём последним — он даёт дефолты, которые можно переопределить
        переменными окружения или .env.
        """
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSource(settings_cls),
            file_secret_settings,
        )


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


@lru_cache
def get_settings() -> Settings:
    return Settings()  # postgres_password обязателен, заполняется из env/secrets.env


settings = get_settings()
