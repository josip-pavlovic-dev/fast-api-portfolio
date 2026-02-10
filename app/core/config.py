from pydantic import BaseModel


class Settings(BaseModel):
    app_env: str = "local"
    database_url: str = ""
    secret_key: str = ""


settings = Settings()
