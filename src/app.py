import io
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for, Response
import os
from conexion import db, init_db

# Configuración de directorio de plantillas
template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'src', 'templates')

# Inicializa la aplicación
app = Flask(__name__, template_folder=template_dir)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///examen.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa la base de datos
init_db(app)

# Modelo de la tabla "creditos"
class Creditos(db.Model):
    __tablename__ = 'creditos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cliente = db.Column(db.String(100), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    tasa_interes = db.Column(db.Float, nullable=False)
    plazo = db.Column(db.Integer, nullable=False)
    fecha_otorgamiento = db.Column(db.String(10), nullable=False)

# Agregar un usuario por defecto al iniciar
with app.app_context():
    db.create_all()
    if not Creditos.query.first():
        nuevo_credito = Creditos(cliente='Juan Pérez', monto=10000, tasa_interes=5.5, plazo=12, fecha_otorgamiento='2025-04-17')
        db.session.add(nuevo_credito)
        db.session.commit()

# Rutas de la aplicación
# Ruta para mostrar el indice
@app.route('/')
def home():
    registros = Creditos.query.all()
    return render_template('index.html', registros=registros)

# Ruta para agregar los reusltados
@app.route('/graficar')
def grafica():
    # Obtener los datos de la base de datos
    registros = Creditos.query.all()
    nombres = [credito.cliente for credito in registros]
    montos = [credito.monto for credito in registros]
    # Crear la gráfica con Matplotlib
    plt.figure(figsize=(8, 4))
    plt.bar(nombres, montos, color='blue', alpha=0.7)
    plt.title('Montos por Cliente')
    plt.xlabel('Clientes')
    plt.ylabel('Montos')
    plt.xticks(rotation=45, ha='right')

    # Guardar la gráfica en un objeto BytesIO
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()  # Cerrar la figura para liberar memoria

    return Response(img.getvalue(), mimetype='image/png')


# Ruta para buscar un usuario
@app.route('/buscar', methods=['GET'])
def buscar_usuario():
    query = request.args.get('query')
    if query:
        resultados = Creditos.query.filter(Creditos.cliente.like(f"%{query}%")).all()
    else:
        resultados = Creditos.query.all()

    return render_template('index.html', registros=resultados, query=query)

# Ruta para mostrar el formulario de crear usuario
@app.route('/new_user', methods=['GET', 'POST'])
def crear_usuario():
    if request.method == 'POST':
        # Obtener datos del formulario
        cliente = request.form['cliente']
        monto = float(request.form['monto'])
        tasa_interes = float(request.form['tasa'])
        plazo = int(request.form['plazo'])
        fecha_otorgamiento = request.form['fecha']

        nuevo_credito = Creditos(
            cliente=cliente,
            monto=monto,
            tasa_interes=tasa_interes,
            plazo=plazo,
            fecha_otorgamiento=fecha_otorgamiento
        )

        db.session.add(nuevo_credito)
        db.session.commit()

        return redirect(url_for('home'))
    return render_template('new_user.html')

# Ruta para editar un usuario
@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def editar_credito(id):
    credito = Creditos.query.get_or_404(id)

    if request.method == 'POST':
        credito.cliente = request.form['cliente']
        credito.monto = float(request.form['monto'])
        credito.tasa_interes = float(request.form['tasa'])
        credito.plazo = int(request.form['plazo'])
        credito.fecha_otorgamiento = request.form['fecha']

        db.session.commit()
        
        return redirect(url_for('home'))

    return render_template('edit_user.html', credito=credito)

# Ruta para eliminar un usuario
@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_credito(id):
    credito = Creditos.query.get_or_404(id)

    db.session.delete(credito)
    db.session.commit()

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=400)
