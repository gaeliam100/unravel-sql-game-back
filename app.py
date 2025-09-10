import os
from flask import Flask, redirect, request
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import datetime
from api_docs.docs_bp import docs_bp  # Esto ya funciona
from config import Config
from db import db

# Importar rutas
from routes.user_routes import user_bp
from routes.auth_routes import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configuración CORS basada en el entorno
    if os.environ.get('FLASK_ENV') == 'production':
        # Para producción - más restrictivo
        CORS(app, 
             origins=["https://unravel-sql.vercel.app"],
             methods=["GET", "POST", "PUT", "DELETE"],
             allow_headers=["Content-Type", "Authorization"],
             supports_credentials=True)
    else:
        # Para desarrollo - más permisivo
        CORS(app, 
             origins=[
                 "https://unravel-sql.vercel.app",
                 "http://localhost:3000",
                 "http://localhost:5173", 
                 "http://localhost:5174",
                 "http://127.0.0.1:3000",
                 "http://127.0.0.1:5173",
                 "http://127.0.0.1:5174"
             ],
             methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
             supports_credentials=True)

    db.init_app(app)
    
    # Inicializar JWT Manager
    jwt = JWTManager(app)

    # Registrar blueprints
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    
    # Swagger solo en desarrollo
    if os.environ.get('FLASK_ENV') != 'production':
        app.register_blueprint(docs_bp, url_prefix="/api")  # Swagger en /api/docs/

    @app.route('/')
    def index():
        if os.environ.get('FLASK_ENV') == 'production':
            return {"message": "Unravel SQL Game API", "status": "running"}
        else:
            return redirect('/api/docs/')

    @app.route('/api/test-cors')
    def test_cors():
        return {
            "message": "CORS test successful",
            "origin": request.headers.get('Origin', 'No Origin header'),
            "user_agent": request.headers.get('User-Agent', 'No User-Agent'),
            "timestamp": datetime.now().isoformat()
        }

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)