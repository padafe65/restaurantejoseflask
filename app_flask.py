from flask import Flask
from flask_cors import CORS

# 1. Importamos los Blueprints desde tus carpetas de routers
from app.routers.user import user_bp
from app.routers.table import table_bp
from app.routers.reservation import reservation_bp
from app.routers.customer import customer_bp

# 2. Creamos la instancia de Flask
app = Flask(__name__)
CORS(app)

# 3. Registro de Blueprints (Equivalente a app.include_router)
# Nota: Primero creamos 'app' y luego registramos
app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(table_bp, url_prefix='/tables')
app.register_blueprint(reservation_bp, url_prefix='/reservations')
app.register_blueprint(customer_bp, url_prefix='/customers')

@app.route("/")
def index():
    return {"mensaje": "Backend MVC en Flask - Restaurante Don José"}

if __name__ == '__main__':
    # Flask corre en el puerto 5000 por defecto
    app.run(debug=True, port=5000)