from flask import Flask
from config import Config
from db import db

# Importar rutas
from routes.user_routes import user_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Registrar blueprints
    app.register_blueprint(user_bp, url_prefix="/api/users")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
