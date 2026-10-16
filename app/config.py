from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "CareerFlow"
    environment: str = "development"
    database_url: str

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


    
