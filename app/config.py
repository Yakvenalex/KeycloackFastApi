import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    KEYCLOAK_BASE_URL: str
    BASE_URL: str
    REALM: str
    CLIENT_ID: str
    CLIENT_SECRET: str
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    @property
    def database_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.BASE_DIR}/data/db.sqlite3"

    # Вычисляемые URL
    @property
    def token_url(self) -> str:
        return f"{self.KEYCLOAK_BASE_URL}/realms/{self.REALM}/protocol/openid-connect/token"

    @property
    def auth_url(self) -> str:
        return (
            f"{self.KEYCLOAK_BASE_URL}/realms/{self.REALM}/protocol/openid-connect/auth"
        )

    @property
    def logout_url(self) -> str:
        return f"{self.KEYCLOAK_BASE_URL}/realms/{self.REALM}/protocol/openid-connect/logout"

    @property
    def userinfo_url(self) -> str:
        return f"{self.KEYCLOAK_BASE_URL}/realms/{self.REALM}/protocol/openid-connect/userinfo"

    @property
    def redirect_uri(self) -> str:
        return f"{self.BASE_URL}/api/login/callback"

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env")


settings = Settings()  # type: ignore
