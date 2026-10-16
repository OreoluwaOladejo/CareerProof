from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "CareerFlow"
    environment: str = "development"
    database_url: str
    secret_key: str
    # The signing algorithm for tokens.
    algorithm: str = "HS256"
    # How long a login token stays valid, in minutes.
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        # Look for environment variables in this file.
        env_file=".env",
        # Read the file using UTF-8.
        env_file_encoding="utf-8",
          # Ignore extra variables in .env that we haven't
        # defined in this Settings class yet.
        extra="ignore",
    
    )
settings =Settings()


    
