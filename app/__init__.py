# __init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# Inicializa SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configuración de la base de datos PostgreSQL con las credenciales de Render
    db_user = os.getenv('DB_USER', 'my_data_electoral_anuer_cortes_p_user')
    db_password = os.getenv('DB_PASSWORD', 'pA8i40oiiGg58OIlHmeyzZWNxAB8b6vh')
    db_host = os.getenv('DB_HOST', 'dpg-crfjmltds78s73co0hc0-a')
    db_name = os.getenv('DB_NAME', 'my_data_electoral_anuer_cortes_p')
    db_port = os.getenv('DB_PORT', '5432')

    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializa SQLAlchemy y Flask-Migrate con la aplicación Flask
    db.init_app(app)
    migrate.init_app(app, db)

    app.secret_key = 'supersecretkey'
    
    from .routes import main
    app.register_blueprint(main)
    
    return app
