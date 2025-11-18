import os
from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    pass


class Config:
    def __init__(self):
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        self.GEMINI_MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemini-2.5-flash")
        self.APP_NAME = os.getenv("APP_NAME", "AI_BLOG_PRODUCTION_AGENT")
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

        # Validate required fields
        self._validate()

    def _validate(self):
        if not self.GOOGLE_API_KEY or self.GOOGLE_API_KEY.strip() == "":
            raise ConfigError(
                "Missing GOOGLE_API_KEY in environment. "
                "Please create a .env file and set GOOGLE_API_KEY="
            )

    def __repr__(self):
        return (
            f"Config(GEMINI_MODEL_ID='{self.GEMINI_MODEL_ID}', "
            f"APP_NAME='{self.APP_NAME}', ENVIRONMENT='{self.ENVIRONMENT}', "
            f"DEBUG_MODE={self.DEBUG_MODE})"
        )


# Create a global instance
config = Config()
