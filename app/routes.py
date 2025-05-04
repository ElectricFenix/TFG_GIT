from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from .models import Acceso, User, Clase, db

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

@main.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/')

    user = User.query.get(user_id)

    limite = request.args.get('limite', default=None, type=int)
    aula_id = request.args.get('aula_id', type=int)
    usuario_id = request.args.get('usuario_id', type=int)

    aulas = Clase.query.all()
    usuarios = User.query.all()

    query = db.session.query(Acceso)

    if aula_id:
        query = query.filter(Acceso.clase_id == aula_id)
    if usuario_id:
        query = query.filter(Acceso.user_id == usuario_id)

    if limite:
        registros = query.order_by(Acceso.accedido.desc()).limit(limite).all()
    else:
        registros = query.order_by(Acceso.accedido.desc()).all()

    if user.rol == 'admin':
        if request.method == 'POST':
            if 'add_user' in request.form:
                nuevo_usuario = request.form['usuario']
                email = request.form['email']
                password = request.form['password']
                rol = request.form['rol']
                nfc = request.form['nfc_uid']
                password_hash = generate_password_hash(password)
                nuevo = User(usuario=nuevo_usuario, email=email, password_hash=password_hash, rol=rol, nfc_uid=nfc)
                db.session.add(nuevo)
                db.session.commit()
                flash('¡Usuario añadido correctamente!', 'success')

            elif 'add_aula' in request.form:
                nombre = request.form['nombre']
                capacidad = request.form['capacidad']
                nueva = Clase(nombre=nombre, capacidad=capacidad)
                db.session.add(nueva)
                db.session.commit()
                flash('¡Aula añadida correctamente!', 'success')

            elif 'delete_user_id' in request.form:
                id_usuario = request.form['delete_user_id']
                usuario_borrar = User.query.get(id_usuario)
                if usuario_borrar and usuario_borrar.id != user.id:
                    db.session.delete(usuario_borrar)
                    db.session.commit()
                    flash('¡Usuario eliminado correctamente!', 'danger')

            elif 'delete_aula_id' in request.form:
                id_aula = request.form['delete_aula_id']
                aula_borrar = Clase.query.get(id_aula)
                if aula_borrar:
                    db.session.delete(aula_borrar)
                    db.session.commit()
                    flash('¡Aula eliminada correctamente!', 'danger')

            return redirect(url_for('main.dashboard'))

        return render_template('dashboard_admin.html', user=user, accesos=registros,
                               aulas=aulas, usuarios=usuarios)

    return render_template('dashboard.html', user=user, accesos=registros,
                           aulas=aulas, usuarios=usuarios)
