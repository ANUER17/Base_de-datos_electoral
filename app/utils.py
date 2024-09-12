from .models import Registro
from . import db

def leer_registros():
    """
    Lee todos los registros de la tabla 'registros'.
    """
    registros = Registro.query.all()
    return registros

def escribir_registro(nuevo_registro):
    """
    Inserta un nuevo registro en la tabla 'registros'.
    nuevo_registro debe ser un diccionario con los campos necesarios.
    """
    registro = Registro(
        cedula=nuevo_registro['cedula'],
        nombres=nuevo_registro['nombres'],
        apellidos=nuevo_registro['apellidos'],
        direccion=nuevo_registro['direccion'],
        numero_contacto=nuevo_registro['numero_contacto'],
        lugar_votacion=nuevo_registro['lugar_votacion'],
        mesa_votacion=nuevo_registro['mesa_votacion'],
        tipo_transporte=nuevo_registro['tipo_transporte'],
        otro_transporte=nuevo_registro.get('otro_transporte', None),
        responsable=nuevo_registro['responsable'],
        codigo_responsable=nuevo_registro.get('codigo_responsable', None)
    )
    db.session.add(registro)
    db.session.commit()

def buscar_registro_por_cedula(cedula):
    """
    Busca un registro por número de cédula.
    """
    return Registro.query.filter_by(cedula=cedula).first()

def modificar_registro(cedula, nuevos_datos):
    """
    Modifica un registro existente por número de cédula con nuevos datos proporcionados.
    nuevos_datos debe ser un diccionario con los campos a actualizar.
    """
    registro = buscar_registro_por_cedula(cedula)
    if registro:
        for key, value in nuevos_datos.items():
            setattr(registro, key, value)
        db.session.commit()

def eliminar_registro(cedula):
    """
    Elimina un registro de la tabla 'registros' por número de cédula.
    """
    registro = buscar_registro_por_cedula(cedula)
    if registro:
        db.session.delete(registro)
        db.session.commit()

def exportar_registros():
    """
    Exporta todos los registros a un archivo CSV.
    """
    import csv
    registros = leer_registros()
    with open('registros_exportados.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Cedula', 'Nombres', 'Apellidos', 'Direccion', 'Numero de Contacto', 'Lugar de Votacion', 
                         'Mesa de Votacion', 'Tipo de Transporte', 'Otro Transporte', 'Responsable', 'Codigo Responsable'])
        for registro in registros:
            writer.writerow([
                registro.cedula, registro.nombres, registro.apellidos, registro.direccion, registro.numero_contacto,
                registro.lugar_votacion, registro.mesa_votacion, registro.tipo_transporte, registro.otro_transporte,
                registro.responsable, registro.codigo_responsable
            ])
    return 'registros_exportados.csv'

def calcular_estadisticas():
    """
    Calcula el número de votos por lugar de votación y el total de votos.
    Ordena las estadísticas de mayor a menor.
    """
    from sqlalchemy import func
    estadisticas = db.session.query(
        Registro.lugar_votacion, func.count(Registro.cedula)
    ).group_by(Registro.lugar_votacion).order_by(func.count(Registro.cedula).desc()).all()

    total_votos = sum([cantidad for _, cantidad in estadisticas])
    estadisticas_ordenadas = {lugar: cantidad for lugar, cantidad in estadisticas}
    
    return estadisticas_ordenadas, total_votos
