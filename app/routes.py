from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from .utils import leer_registros, escribir_registro, buscar_registro_por_cedula, modificar_registro, eliminar_registro, exportar_registros, calcular_estadisticas
import os

main = Blueprint('main', __name__)

EXPORT_FILE = os.path.join(os.getcwd(), 'registros_exportados.csv')  # Ruta completa para el archivo de exportación
CLAVE_MODIFICAR = '2027'
CLAVE_ELIMINAR = '2027'
CLAVE_EXPORTAR = 'neguibalcalde20282031'
CLAVE_ESTADISTICAS = 'neguibalcalde20282031'  # Clave para ver estadísticas

def obtener_codigos_responsables():
    """Función para obtener los códigos de responsables existentes y únicos."""
    registros = leer_registros()
    codigos_responsables = {registro.codigo_responsable for registro in registros if registro.responsable == 'SI' and registro.codigo_responsable}
    return sorted(codigos_responsables)

def obtener_mesas_por_lugar(lugar_votacion):
    """Función para obtener las mesas según el lugar de votación."""
    mesas_por_lugar = {
        'Cabecera Municipal': 21,
        'Micoahumado': 4,
        'Bodega Central': 3,
        'El Dique': 3,
        'La Palma': 2,
        'Boca de La Honda': 2,
        'Las Pailas': 2,
        'Corcovado': 2,
        'La Esmeralda': 1,
        'Paredes de Ororia': 1,
        'Mina Gallo': 1
    }
    max_mesas = mesas_por_lugar.get(lugar_votacion, 1)
    return [f"Mesa {i}" for i in range(1, max_mesas + 1)]

# Ruta para el inicio de sesión
@main.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == '1717':
            session['logged_in'] = True
            flash('Has ingresado con éxito.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Usuario y/o contraseña incorrecto.', 'error')
    return render_template('login.html')

# Ruta principal (panel principal)
@main.route('/index')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))
    
    return render_template('index.html')

# Ruta para mostrar estadísticas de votación
@main.route('/estadisticas', methods=['GET', 'POST'])
def estadisticas():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        clave = request.form['clave']
        if clave == CLAVE_ESTADISTICAS:
            estadisticas_votos, total_votos = calcular_estadisticas()
            return render_template('estadisticas.html', estadisticas=estadisticas_votos, total_votos=total_votos)
        else:
            flash('Clave incorrecta para ver estadísticas.', 'error')
            return redirect(url_for('main.index'))
    
    return render_template('estadisticas.html', estadisticas=None, total_votos=0)

# Ruta para registrar un nuevo registro
@main.route('/registro', methods=['GET', 'POST'])
def registro():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))

    # Obtener los códigos de responsables existentes
    codigos_responsables = obtener_codigos_responsables()
    
    if request.method == 'POST':
        nuevo_registro = {
            'cedula': request.form['cedula'],
            'nombres': request.form['nombres'],
            'apellidos': request.form['apellidos'],
            'direccion': request.form['direccion'],
            'numero_contacto': request.form['numero_contacto'],
            'lugar_votacion': request.form['lugar_votacion'],
            'mesa_votacion': request.form['mesa_votacion'],
            'tipo_transporte': request.form['tipo_transporte'],
            'otro_transporte': request.form.get('otro_transporte_input', ''),
            'responsable': request.form['responsable'],
            'codigo_responsable': request.form.get('codigo_responsable') or request.form.get('seleccionar_codigo')
        }

        # Verificar si la cédula ya existe
        if buscar_registro_por_cedula(nuevo_registro['cedula']):
            flash('Este número de cédula ya fue registrado.', 'error')
        else:
            # Verificar si el código de responsable es único
            if nuevo_registro['responsable'] == 'SI' and nuevo_registro['codigo_responsable'] in codigos_responsables:
                flash('El código de responsable ya está asignado a otra persona.', 'error')
            else:
                escribir_registro(nuevo_registro)
                flash('Registro guardado exitosamente.', 'success')
                return redirect(url_for('main.index'))
    
    return render_template('registro.html', codigos_responsables=codigos_responsables)

# Ruta para buscar registros
@main.route('/cargar_busqueda', methods=['POST'])
def cargar_busqueda():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))

    # Limpiar mensajes de exportación en otras rutas
    session.pop('export_success', None)
    
    cedula = request.form['cedula']
    registro = buscar_registro_por_cedula(cedula)

    if registro:
        # Renderizar la plantilla con el registro encontrado
        return render_template('index.html', registro=registro, action='buscar')
    else:
        flash('Este registro no se encuentra en la base de datos.', 'error')
        return redirect(url_for('main.index'))

# Ruta para cargar datos del registro para modificar
@main.route('/cargar_modificacion', methods=['POST'])
def cargar_modificacion():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))
    
    cedula = request.form['cedula']
    registro = buscar_registro_por_cedula(cedula)
    codigos_responsables = obtener_codigos_responsables()
    
    if registro:
        # Verificar si el registro es de un responsable
        if registro.responsable == 'SI':
            flash('No se puede modificar un registro que es un responsable.', 'error')
            return redirect(url_for('main.index'))
        
        # Obtener las mesas según el lugar de votación
        mesas_votacion = obtener_mesas_por_lugar(registro.lugar_votacion)

        return render_template('index.html', registro=registro, action='modificar', codigos_responsables=codigos_responsables, mesas_votacion=mesas_votacion)
    else:
        flash('Registro no encontrado para modificar.', 'error')
        return redirect(url_for('main.index'))

# Ruta para guardar los cambios en el registro modificado
@main.route('/guardar_modificacion', methods=['POST'])
def guardar_modificacion():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))
    
    cedula = request.form['cedula']
    nuevos_datos = {
        'nombres': request.form['nombres'],
        'apellidos': request.form['apellidos'],
        'direccion': request.form['direccion'],
        'numero_contacto': request.form['numero_contacto'],
        'lugar_votacion': request.form['lugar_votacion'],
        'mesa_votacion': request.form.get('mesa_votacion'),
        'tipo_transporte': request.form['tipo_transporte'],
        'otro_transporte': request.form.get('otro_transporte_input', ''),
        'responsable': request.form.get('responsable', 'NO'),
        'codigo_responsable': request.form.get('codigo_responsable') if request.form.get('responsable') == 'SI' else request.form.get('seleccionar_codigo')
    }

    # Verificar si el código de responsable es único solo si es 'SI'
    if nuevos_datos['responsable'] == 'SI' and nuevos_datos['codigo_responsable'] in obtener_codigos_responsables() and nuevos_datos['codigo_responsable'] != buscar_registro_por_cedula(cedula).codigo_responsable:
        flash('El código de responsable ya está asignado a otra persona.', 'error')
        return redirect(url_for('main.index'))
    else:
        # Guardar los cambios en el registro
        modificar_registro(cedula, nuevos_datos)
        flash('Registro modificado exitosamente.', 'success')

    return redirect(url_for('main.index'))

# Ruta para cargar datos para eliminar
@main.route('/cargar_eliminar', methods=['POST'])
def cargar_eliminar():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))
    
    cedula = request.form['cedula']
    registro = buscar_registro_por_cedula(cedula)
    
    if registro:
        return render_template('index.html', registro=registro, action='eliminar')
    else:
        flash('Registro no encontrado para eliminar.', 'error')
        return redirect(url_for('main.index'))

# Ruta para eliminar registros
@main.route('/eliminar', methods=['POST'])
def eliminar():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))
    
    if request.form.get('confirmar') == 'true':
        cedula = request.form['cedula']
        eliminar_registro(cedula)
        flash('Registro eliminado exitosamente.', 'success')
    return redirect(url_for('main.index'))

# Ruta para exportar registros y descargar el archivo directamente
@main.route('/exportar', methods=['POST'])
def exportar():
    if not session.get('logged_in'):
        return redirect(url_for('main.login'))
    
    clave = request.form['clave']
    
    if clave != CLAVE_EXPORTAR:
        flash('Clave incorrecta para exportar registros.', 'error')
        return redirect(url_for('main.index'))
    
    if exportar_registros():
        return send_file(EXPORT_FILE, as_attachment=True, download_name='registros_exportados.csv')
    else:
        flash('Error al exportar los registros.', 'error')
        return redirect(url_for('main.index'))

# Ruta para cerrar sesión
@main.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('main.login'))
