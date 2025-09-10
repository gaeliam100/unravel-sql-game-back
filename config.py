import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = os.environ.get('JWT_COOKIE_SECURE', 'False').lower() == 'true'
    JWT_COOKIE_CSRF_PROTECT = os.environ.get('JWT_COOKIE_CSRF_PROTECT', 'False').lower() == 'true'
    JWT_COOKIE_SAMESITE = os.environ.get('JWT_COOKIE_SAMESITE', 'Lax')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_HOURS', 1)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES_DAYS', 30)))
    JWT_ACCESS_COOKIE_NAME = 'access_token_cookie'
    JWT_REFRESH_COOKIE_NAME = 'refresh_token_cookie'
    DATABASE_URL = os.environ.get('DATABASE_URL')