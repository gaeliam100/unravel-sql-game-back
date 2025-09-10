import os
from flask import Flask, redirect
from flask_jwt_extended import JWTManager
from api_docs.docs_bp import docs_bp  # Esto ya funciona
from config import Config
from db import db

# Importar rutas
from routes.user_routes import user_bp
from routes.auth_routes import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    
    # Inicializar JWT Manager
    jwt = JWTManager(app)

    # Registrar blueprints
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(docs_bp, url_prefix="/api")  # Swagger en /api/docs/

    @app.route('/')
    def index():
        # Redirige automáticamente a Swagger
        return redirect('/api/docs/')

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)