import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///./test.db'  # Local SQLite DB
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
    ALGORITHM = "HS256"
    TOKEN_EXP_LIMIT = 30
    PWD_CRYPTO_SCHEMA = "argon2"
    PWD_CRYPTO_DEPRECATED = "auto"