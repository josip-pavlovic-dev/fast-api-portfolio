import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Učitava varijable iz .env fajla ako postoji.
load_dotenv()


@dataclass(frozen=True)
class Settings:
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int


def get_settings() -> Settings:
    jwt_secret_key = os.getenv("JWT_SECRET_KEY")
    if not jwt_secret_key:
        raise RuntimeError(
            "JWT_SECRET_KEY nije postavljen. Dodaj ga u environment ili .env fajl."
        )

    jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")

    expire_minutes_raw = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "20")
    try:
        access_token_expire_minutes = int(expire_minutes_raw)
    except ValueError as error:
        raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES mora biti ceo broj.") from error

    if access_token_expire_minutes <= 0:
        raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES mora biti > 0.")

    return Settings(
        jwt_secret_key=jwt_secret_key,
        jwt_algorithm=jwt_algorithm,
        access_token_expire_minutes=access_token_expire_minutes,
    )


settings = get_settings()
