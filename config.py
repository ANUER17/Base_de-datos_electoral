# config.py
import os

DB_HOST = os.getenv('DB_HOST', 'dpg-crfjmltds78s73co0hc0-a')
DB_NAME = os.getenv('DB_NAME', 'my_data_electoral_anuer_cortes_p')
DB_USER = os.getenv('DB_USER', 'my_data_electoral_anuer_cortes_p_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'pA8i40oiiGg58OIlHmeyzZWNxAB8b6vh')
DB_PORT = os.getenv('DB_PORT', '5432')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
