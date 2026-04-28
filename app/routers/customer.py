from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.customer import Customer
from app.auth import get_current_user 

customer_bp = Blueprint('customer', __name__)

# --- LISTAR CLIENTES ---
@customer_bp.route("/", methods=["GET"])
def get_customers():
    current_user = get_current_user()
    if not current_user:
        return jsonify({"detail": "No autorizado"}), 401
        
    db = next(get_db())
    try:
        # Si es cliente, solo le devolvemos su propia ficha por seguridad
        if current_user.role == "cliente":
            customers = db.query(Customer).filter(Customer.user_id == current_user.id).all()
        else:
            customers = db.query(Customer).all()
            
        return jsonify([{
            "id": c.id,
            "user_id": c.user_id,
            "full_name": c.full_name,
            "phone": c.phone,
            "whatsapp": c.whatsapp,
            "address": c.address
        } for c in customers]), 200
    finally:
        db.close()

# --- CREAR CLIENTE ---
@customer_bp.route("/", methods=["POST"])
def create_customer():
    current_user = get_current_user()
    if not current_user or current_user.role == "cliente":
        return jsonify({"detail": "Operación no permitida"}), 403
    
    data = request.json
    db = next(get_db())
    try:
        new_customer = Customer(
            user_id=data.get('user_id'),
            full_name=data.get('full_name'),
            phone=data.get('phone'),
            whatsapp=data.get('whatsapp'),
            address=data.get('address')
        )
        
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
        
        return jsonify({
            "id": new_customer.id,
            "full_name": new_customer.full_name,
            "user_id": new_customer.user_id
        }), 201
    except Exception as e:
        db.rollback()
        print(f"Error al crear cliente: {e}")
        return jsonify({"detail": "Error al crear el perfil del cliente"}), 500
    finally:
        db.close()

# --- ACTUALIZAR CLIENTE ---
@customer_bp.route("/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    current_user = get_current_user()
    if not current_user:
        return jsonify({"detail": "No autorizado"}), 401
        
    db = next(get_db())
    try:
        customer_query = db.query(Customer).filter(Customer.id == customer_id)
        customer = customer_query.first()
        
        if not customer:
            return jsonify({"detail": "Cliente no encontrado"}), 404
        
        # Seguridad: Admin, Mesero o el propio dueño
        if current_user.role not in ["admin", "mesero"] and current_user.id != customer.user_id:
            return jsonify({"detail": "No tienes permiso para editar este perfil"}), 403
        
        data = request.json
        customer_query.update(data, synchronize_session=False)
        db.commit()
        
        return jsonify({"mensaje": "Perfil actualizado exitosamente"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"detail": str(e)}), 500
    finally:
        db.close()

# --- ELIMINAR CLIENTE (Solo Admin) ---
@customer_bp.route("/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    current_user = get_current_user()
    if not current_user or current_user.role != "admin":
        return jsonify({"detail": "Solo el administrador jefe puede eliminar perfiles"}), 403
    
    db = next(get_db())
    try:
        customer_query = db.query(Customer).filter(Customer.id == customer_id)
        
        if not customer_query.first():
            return jsonify({"detail": "Cliente no encontrado"}), 404
        
        customer_query.delete(synchronize_session=False)
        db.commit()
        return '', 204
    except Exception as e:
        db.rollback()
        return jsonify({"detail": "Error al eliminar cliente"}), 500
    finally:
        db.close()