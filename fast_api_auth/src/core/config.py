from logging import config as logging_config

from pydantic import EmailStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .logger import LOGGING_CONFIG


logging_config.dictConfig(LOGGING_CONFIG)


class ProjectSettings(BaseSettings):
    """Настройки проекта."""

    project_auth_name: str
    project_auth_summary: str
    project_auth_tags: list = Field(
        default=[
            {
                'name': 'auth',
                'description': 'Operations with auth.',
            },
            {
                'name': 'users',
                'description': 'Operations with users.',
            },
            {
                'name': 'roles',
                'description': 'Operations with roles.',
            },
        ]
    )

    # Redis
    redis_host: str
    redis_port: int
    redis_user: str
    redis_password: str
    redis_db_index: int
    redis_dsn: str = ''

    # Postgres
    postgres_db_name: str
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_dsn: str = ''

    # Auth
    secret: str
    first_superuser_email: EmailStr | None = None
    first_superuser_password: str | None = None
    jwt_lifetime_seconds: int = 3600
    jwt_refresh_lifetime_seconds: int = 86400
    min_password_length: int = 3

    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )
    debug: bool = False


class RedisSettings(BaseSettings):
    """Настройки Redis."""

    host: str
    port: int
    user: str
    password: str
    db_index: int
    dsn: str = ''

    model_config = SettingsConfigDict(
        env_file='.env', extra='ignore', env_prefix='REDIS_'
    )

    def model_post_init(self, __context: any) -> None:
        """Формируем DSN после загрузки переменных."""
        self.dsn = f'redis://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_index}'


class PostgresSettings(BaseSettings):
    """Настройки Postgres."""

    db_name: str
    host: str
    port: int
    user: str
    password: str
    dsn: str = ''

    model_config = SettingsConfigDict(
        env_file='.env', extra='ignore', env_prefix='POSTGRES_'
    )

    def model_post_init(self, __context: any) -> None:
        """Формируем DSN после загрузки переменных."""
        self.dsn = f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}'


class AuthSettings(BaseSettings):
    """Настройки авторизации."""

    secret: str
    first_superuser_email: EmailStr | None = None
    first_superuser_password: str | None = None
    jwt_lifetime_seconds: int = 3600
    min_password_lenght: int = 3

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


project_settings = ProjectSettings()
redis_settings = RedisSettings()
postgres_settings = PostgresSettings()
auth_settings = AuthSettings()
