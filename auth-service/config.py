import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///auth.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Shared secret admin-service must present to call the /internal/* routes.
    INTERNAL_SERVICE_KEY = os.getenv("INTERNAL_SERVICE_KEY", "dev-INTERNAL_SERVICE_KEY")
