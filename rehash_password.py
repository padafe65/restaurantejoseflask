"""
Script para rehashear contraseña de usuario en la BD
Usa la misma configuración de Bcrypt del proyecto
"""
from app.extensions import bcrypt
from app.database import SessionLocal
# Importar todos los modelos para que SQLAlchemy conozca las relaciones
from app.models.user import User
from app.models.customer import Customer
from app.models.reservation import Reservation
from app.models.table import Table

# Contraseña a hashear
password = "123456"

# Hashear con Bcrypt
hashed = bcrypt.generate_password_hash(password).decode('utf-8')
print(f"Hash generado: {hashed}")

# Actualizar en BD
db = SessionLocal()
try:
    user = db.query(User).filter(User.email == "pedro@restaurante.com").first()
    if user:
        user.password_hash = hashed
        db.commit()
        print(f"✅ Contraseña actualizada para: {user.username}")
    else:
        print("❌ Usuario no encontrado")
finally:
    db.close()
