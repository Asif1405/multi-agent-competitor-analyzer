from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    # app
    APP_NAME: str = "Multi Agent LLM"
    APP_DESCRIPTION: str = ("Gradio App for generating competitor analysis reports using OpenAI's GPT-4o.")
    APP_VERSION: str = "0.0.1"


    # OpenAI API key
    OPENAI_API_KEY: str = Field(...
                                , env="OPENAI_API_KEY")

settings = Settings()
