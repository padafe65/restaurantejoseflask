from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.customer import Customer
from app.auth import create_access_token, get_current_user 
from app.extensions import bcrypt
import datetime

# Definimos el Blueprint (El Router de Flask)
user_bp = Blueprint('user', __name__)

# --- LOGIN (Para obtener el Token) ---
@user_bp.route("/login", methods=["POST"])
def login():
    print("\n--- Intento de Login Detectado ---")
    data = request.json
    email = data.get('username')
    password = data.get('password')
    
    print(f"Probando con el correo: {email}")

    db = next(get_db())
    try:
        user = db.query(User).filter(User.email == email).first()

        if not user:
            print("❌ Error: El usuario no existe en la base de datos.")
            return jsonify({"detail": "Credenciales incorrectas"}), 401

        print(f"Usuario encontrado: {user.username}. Verificando contraseña...")
        print(f"DEBUG - Hash en DB: {user.password_hash[:30]}...")
        print(f"DEBUG - Contraseña ingresada: {password}")

        # Verificamos la clave
        is_valid = bcrypt.check_password_hash(user.password_hash, password)
        print(f"DEBUG - Resultado verificación: {is_valid}")

        if is_valid:
            print("✅ ¡Contraseña correcta! Generando token...")
            token = create_access_token(data={"sub": user.email})
            return jsonify({
                "access_token": token,
                "token_type": "bearer",
                "user_id": user.id,
                "role": user.role
            }), 200
        else:
            print("❌ Error: La contraseña no coincide.")
            return jsonify({"detail": "Credenciales incorrectas"}), 401
    finally:
        db.close()


# --- CREAR USUARIO CON CLIENTE AUTOMÁTICO ---
@user_bp.route("/", methods=["POST"])
def create_user():
    db = next(get_db())
    try:
        existing_user = db.query(User).filter(User.email == data.get('email')).first()
        if existing_user:
            return jsonify({"detail": "El email ya está registrado"}), 400
        
        hashed_password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
        
        # 1. Crear el Usuario
        new_user = User(
            username=data.get('username'),
            email=data.get('email'),
            password_hash=hashed_password,
            role=data.get('role', 'cliente'),
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # 2. CREAR FICHA DE CLIENTE AUTOMÁTICAMENTE
        if new_user.role == "cliente":
            new_customer = Customer(
                user_id=new_user.id,
                full_name=new_user.username,
                phone="S/N",
                whatsapp="S/N",
                address="Pendiente"
            )
            db.add(new_customer)
            db.commit()
        
        return jsonify({
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role,
            "created_at": new_user.created_at.isoformat(),
            "is_active": new_user.is_active
        }), 201
    finally:
        db.close()

# --- LISTAR TODOS ---
@user_bp.route("/", methods=["GET"])
def get_users():
    db = next(get_db())
    try:
        users = db.query(User).all()
        return jsonify([{
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat()
        } for u in users]), 200
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        return jsonify({"detail": "Error al obtener usuarios"}), 500
    finally:
        db.close()

# --- BUSCAR UNO POR ID ---
@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    db = next(get_db())
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({"detail": "Usuario no encontrado"}), 404
        
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        }), 200
    finally:
        db.close()

# --- ACTUALIZAR ---
@user_bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.json
    db = next(get_db())
    try:
        user_query = db.query(User).filter(User.id == user_id)
        user = user_query.first()
        
        if not user:
            return jsonify({"detail": "Usuario no encontrado"}), 404
        
        update_data = {}
        if "username" in data: update_data["username"] = data["username"]
        if "email" in data: update_data["email"] = data["email"]
        if "is_active" in data: update_data["is_active"] = data["is_active"]
        if "role" in data: update_data["role"] = data["role"]
        
        if "password" in data and data["password"]:
            update_data["password_hash"] = bcrypt.generate_password_hash(data["password"]).decode('utf-8')
        
        user_query.update(update_data, synchronize_session=False)
        db.commit()
        return jsonify({"mensaje": "Usuario actualizado exitosamente"}), 200
    finally:
        db.close()

# --- ELIMINAR (SOLO ADMIN) ---
@user_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    db = next(get_db())
    try:
        user_query = db.query(User).filter(User.id == user_id)
        user = user_query.first()
        
        if not user:
            return jsonify({"detail": "Usuario no encontrado"}), 404
        
        user_query.delete(synchronize_session=False)
        db.commit()
        return '', 204
    finally:
        db.close()