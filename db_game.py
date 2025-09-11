import os

def _env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return str(val).lower() in {"1", "true", "yes", "y", "on"}

def _build_sqlalchemy_uri() -> str:
    engine = os.getenv("DB_ENGINE", "mysql").lower()

    if engine == "sqlite":
        # sqlite local para pruebas rápidas
        db_path = os.getenv("DB_NAME", "app.db")
        return f"sqlite:///{db_path}"

    user = os.getenv("DB_USER", "root")
    pwd  = os.getenv("DB_PASS", "")
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", "3306"))
    name = os.getenv("DB_NAME", "unravel_game")

    if engine == "mysql":
        # usa mysql-connector-python
        return f"mysql+mysqlconnector://{user}:{pwd}@{host}:{port}/{name}?charset=utf8mb4"
    elif engine == "postgresql":
        # por si decides usar Postgres (psycopg2-binary)
        port = int(os.getenv("DB_PORT", "5432"))
        return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{name}"
    else:
        raise ValueError(f"DB_ENGINE no soportado: {engine}")

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = _build_sqlalchemy_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pooling
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "1800"))  # seg
    DB_POOL_PRE_PING = _env_bool("DB_POOL_PRE_PING", True)

    # Pasar opciones al engine de SQLAlchemy
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": DB_POOL_SIZE,
        "max_overflow": DB_MAX_OVERFLOW,
        "pool_recycle": DB_POOL_RECYCLE,
        "pool_pre_ping": DB_POOL_PRE_PING,
    }

class DevelopmentConfig(BaseConfig):
    DEBUG = True

class TestingConfig(BaseConfig):
    TESTING = True
    # DB de test en memoria si usas sqlite
    if os.getenv("DB_ENGINE", "mysql").lower() == "sqlite":
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class ProductionConfig(BaseConfig):
    DEBUG = False

def get_config():
    env = os.getenv("FLASK_ENV", "development").lower()
    return {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }.get(env, DevelopmentConfig)
