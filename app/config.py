from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """
    host: str = Field(default="0.0.0.0", validation_alias="HOST")
    port: int = Field(default=8000, validation_alias="PORT")
    
    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    openai_model_name: str = Field(default="gpt-4o-mini", validation_alias="OPENAI_MODEL_NAME")
    
    embedding_model_name: str = Field(default="all-MiniLM-L6-v2", validation_alias="EMBEDDING_MODEL_NAME")
    
    tickets_file_path: str = Field(default="data/tickets.json", validation_alias="TICKETS_FILE_PATH")
    accounts_file_path: str = Field(default="data/accounts.json", validation_alias="ACCOUNTS_FILE_PATH")
    kb_directory_path: str = Field(default="knowledge-base", validation_alias="KB_DIRECTORY_PATH")
    faiss_index_path: str = Field(default="data/faiss_index", validation_alias="FAISS_INDEX_PATH")
    tickets_index_path: str = Field(default="data/tickets_index", validation_alias="TICKETS_INDEX_PATH")

    # SettingsConfigDict specifies loading from .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
