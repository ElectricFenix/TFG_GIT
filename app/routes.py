from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_
from .models import Acceso, User, Clase, Reserva, db
from datetime import datetime
import pytz

zona_es = pytz.timezone('Europe/Madrid')


main = Blueprint('main', __name__)

# Página de login
@main.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        user = User.query.filter_by(usuario=usuario).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            return redirect(url_for('main.dashboard'))
        else:
            error = 'Usuario o contraseña incorrectos.'

    return render_template('login.html', error=error)

# Cerrar sesión
@main.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.login'))

from datetime import datetime

@main.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/')

    user = User.query.get(user_id)

    limite = request.args.get('limite', default=10, type=int)
    aula_id = request.args.get('aula_id', type=int)
    usuario_id = request.args.get('usuario_id', type=int)

    limite_reservas = request.args.get('limite_reservas', default=10, type=int)
    fecha_reserva_desde_str = request.args.get('fecha_reserva_desde')
    fecha_reserva_hasta_str = request.args.get('fecha_reserva_hasta')
    reserva_aula_id = request.args.get('reserva_aula_id', type=int)
    reserva_usuario_id = request.args.get('reserva_usuario_id', type=int)

    usuario_filtro = request.args.get('usuario_filtro', type=int)
    limite_usuarios = request.args.get('limite_usuarios', default=10, type=int)

    clase_filtro = request.args.get('clase_filtro', type=int)
    limite_clases = request.args.get('limite_clases', default=10, type=int)

    aulas = Clase.query.all()
    usuarios = User.query.all()

    query = db.session.query(Acceso)
    if aula_id:
        query = query.filter(Acceso.clase_id == aula_id)
    if usuario_id:
        query = query.filter(Acceso.user_id == usuario_id)
    registros = query.order_by(Acceso.accedido.desc()).limit(limite).all()

    reserva_query = db.session.query(Reserva)
    if reserva_usuario_id:
        reserva_query = reserva_query.filter(Reserva.user_id == reserva_usuario_id)
    if reserva_aula_id:
        reserva_query = reserva_query.filter(Reserva.clase_id == reserva_aula_id)

    if fecha_reserva_desde_str:
        try:
            reserva_desde = datetime.strptime(fecha_reserva_desde_str, '%Y-%m-%d')
            reserva_query = reserva_query.filter(Reserva.fecha_reserva_desde >= reserva_desde)
        except ValueError:
            pass

    if fecha_reserva_hasta_str:
        try:
            reserva_hasta = datetime.strptime(fecha_reserva_hasta_str, '%Y-%m-%d')
            reserva_query = reserva_query.filter(Reserva.fecha_reserva_desde <= reserva_hasta)
        except ValueError:
            pass

    reservas = reserva_query.order_by(Reserva.fecha_reserva_desde.desc()).limit(limite_reservas).all()

    usuarios_query = db.session.query(User)
    if usuario_filtro:
        usuarios_query = usuarios_query.filter(User.id == usuario_filtro)
    usuarios_mostrar = usuarios_query.order_by(User.usuario).limit(limite_usuarios).all()

    aulas_query = db.session.query(Clase)
    if clase_filtro:
        aulas_query = aulas_query.filter(Clase.id == clase_filtro)
    aulas_mostrar = aulas_query.order_by(Clase.nombre).limit(limite_clases).all()

    if request.method == 'POST':
        if user.rol == 'admin':
            if 'add_user' in request.form:
                nuevo_usuario = request.form['usuario']
                email = request.form['email']
                password = request.form['password']
                rol = request.form['rol']
                nfc = request.form['nfc_uid']
                password_hash = generate_password_hash(password)

                nuevo = User(usuario=nuevo_usuario, email=email, password_hash=password_hash, rol=rol, nfc_uid=nfc)
                db.session.add(nuevo)
                try:
                    db.session.commit()
                    flash('¡Usuario añadido correctamente!', 'success')
                except IntegrityError:
                    db.session.rollback()
                    flash('Ya existe un usuario con ese nombre, correo o NFC.', 'danger')

            elif 'add_aula' in request.form:
                nombre = request.form['nombre']
                capacidad = request.form['capacidad']
                descripcion = request.form.get('descripcion', '')
                nueva = Clase(nombre=nombre, capacidad=capacidad, descripcion=descripcion)
                db.session.add(nueva)
                try:
                    db.session.commit()
                    flash('¡Aula añadida correctamente!', 'success')
                except IntegrityError:
                    db.session.rollback()
                    flash('Ya existe un aula con ese nombre.', 'danger')

            elif 'delete_user_id' in request.form:
                id_usuario = request.form['delete_user_id']
                usuario_borrar = User.query.get(id_usuario)
                if usuario_borrar and usuario_borrar.id != user.id:
                    db.session.delete(usuario_borrar)
                    db.session.commit()
                    flash('¡Usuario eliminado correctamente!', 'sucess')

            elif 'delete_aula_id' in request.form:
                id_aula = request.form['delete_aula_id']
                aula_borrar = Clase.query.get(id_aula)
                if aula_borrar:
                    db.session.delete(aula_borrar)
                    db.session.commit()
                    flash('¡Aula eliminada correctamente!', 'sucess')

            elif 'delete_reserva_id' in request.form:
                reserva_id = request.form['delete_reserva_id']
                reserva = Reserva.query.get(reserva_id)
                if reserva:
                    db.session.delete(reserva)
                    db.session.commit()
                    flash('¡Reserva eliminada correctamente!', 'success')

        if 'make_reservation' in request.form:
            aula_id = request.form.get('reserva_aula_id')
            fecha_desde_str = request.form.get('fecha_reserva_desde')
            fecha_hasta_str = request.form.get('fecha_reserva_hasta')

            try:
                fecha_desde = datetime.strptime(fecha_desde_str, '%Y-%m-%dT%H:%M').replace(tzinfo=zona_es)
                fecha_hasta = datetime.strptime(fecha_hasta_str, '%Y-%m-%dT%H:%M').replace(tzinfo=zona_es)
                ahora = datetime.now(zona_es)

                if fecha_desde <= ahora:
                    flash('La fecha/hora de inicio debe ser en el futuro.', 'warning')

                elif fecha_desde >= fecha_hasta:
                    flash('La fecha/hora de inicio debe ser anterior a la de fin.', 'warning')

                else:
                    reservas_solapadas = Reserva.query.filter(
                        Reserva.clase_id == aula_id,
                        or_(
                            and_(Reserva.fecha_reserva_desde <= fecha_desde, Reserva.fecha_reserva_hasta > fecha_desde),
                            and_(Reserva.fecha_reserva_desde < fecha_hasta, Reserva.fecha_reserva_hasta >= fecha_hasta),
                            and_(Reserva.fecha_reserva_desde >= fecha_desde, Reserva.fecha_reserva_hasta <= fecha_hasta),
                        )
                    ).all()

                    if reservas_solapadas:
                        flash('Ya existe una reserva que se solapa con las fechas seleccionadas.', 'danger')
                    else:
                        nueva_reserva = Reserva(
                            user_id=user.id,
                            clase_id=aula_id,
                            fecha_reserva_desde=fecha_desde,
                            fecha_reserva_hasta=fecha_hasta
                        )
                        db.session.add(nueva_reserva)
                        db.session.commit()
                        flash('¡Reserva creada con éxito!', 'success')

            except ValueError:
                flash('Formato de fecha/hora inválido.', 'danger')

        if 'delete_reserva_id' in request.form:
            reserva_id = request.form.get('delete_reserva_id')
            reserva = Reserva.query.get(reserva_id)
            if reserva and reserva.user_id == user.id:
                db.session.delete(reserva)
                db.session.commit()
                flash('¡Reserva eliminada correctamente!', 'success')
            else:
                flash('No tienes permiso para eliminar esta reserva.', 'danger')

        return redirect(url_for('main.dashboard'))

    if user.rol == 'admin':
        return render_template(
            'dashboard_admin.html',
            user=user,
            accesos=registros,
            aulas=aulas,
            usuarios=usuarios,
            reservas=reservas,
            usuarios_mostrar=usuarios_mostrar,
            aulas_mostrar=aulas_mostrar
        )

    return render_template(
        'dashboard.html',
        user=user,
        accesos=registros,
        aulas=aulas,
        usuarios=usuarios,
        reservas=reservas
    )
