from functools import lru_cache
from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    #
    # Pydantic will look for 'USER_TOKEN_SECRET' in your environment or .env
    # It automatically converts the string to a SecretStr
    user_token_secret: SecretStr = SecretStr("placeholder-value")
    

    # This tells Pydantic to read from the .env file
    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings():
    """Returns a cached instance of the settings."""
    return Settings()