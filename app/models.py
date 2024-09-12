# models.py
from . import db

class Registro(db.Model):
    __tablename__ = 'registros'
    cedula = db.Column(db.String(20), primary_key=True)
    nombres = db.Column(db.String(100))
    apellidos = db.Column(db.String(100))
    direccion = db.Column(db.String(150))
    numero_contacto = db.Column(db.String(15))
    lugar_votacion = db.Column(db.String(100))
    mesa_votacion = db.Column(db.String(20))
    tipo_transporte = db.Column(db.String(50))
    otro_transporte = db.Column(db.String(50))
    responsable = db.Column(db.String(2))
    codigo_responsable = db.Column(db.String(20))
