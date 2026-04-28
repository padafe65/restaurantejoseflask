from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.table import Table
from app.auth import get_current_user 

table_bp = Blueprint('table', __name__)

# --- OBTENER TODAS LAS MESAS ---
@table_bp.route("/", methods=["GET"])
def get_tables():
    db = next(get_db())
    try:
        tables = db.query(Table).all()
        return jsonify([{
            "id": t.id,
            "number": t.number,
            "capacity": t.capacity,
            "status": t.status
        } for t in tables]), 200
    finally:
        db.close()

# --- CREAR MESA (Solo Admin) ---
@table_bp.route("/", methods=["POST"])
def create_table():
    current_user = get_current_user()
    if current_user.role != "admin":
        return jsonify({"detail": "Solo el administrador puede crear mesas"}), 403
    
    data = request.json
    db = next(get_db())
    try:
        new_table = Table(
            number=data.get('number'),
            capacity=data.get('capacity'),
            status=data.get('status', 'libre')
        )
        db.add(new_table)
        db.commit()
        db.refresh(new_table)
        return jsonify({"id": new_table.id, "number": new_table.number, "status": new_table.status}), 201
    finally:
        db.close()

# --- ACTUALIZAR MESA COMPLETA (PUT - Solo Admin) ---
@table_bp.route("/<int:table_id>", methods=["PUT"])
def update_table(table_id):
    current_user = get_current_user()
    if current_user.role != "admin":
        return jsonify({"detail": "Solo el administrador puede editar mesas"}), 403
    
    data = request.json
    db = next(get_db())
    try:
        table_query = db.query(Table).filter(Table.id == table_id)
        table = table_query.first()
        
        if not table:
            return jsonify({"detail": "Mesa no encontrada"}), 404
        
        table_query.update(data, synchronize_session=False)
        db.commit()
        return jsonify({"id": table.id, "number": table.number, "status": table.status}), 200
    finally:
        db.close()

# --- ACTUALIZAR ESTADO (PATCH - Admin y Mesero) ---
@table_bp.route("/<int:table_id>/status", methods=["PATCH"])
def update_table_status(table_id):
    current_user = get_current_user()
    if current_user.role not in ["admin", "mesero"]:
        return jsonify({"detail": "No tienes permisos"}), 403
    
    data = request.json
    nuevo_status = data.get("status")
    
    if nuevo_status not in ["libre", "reservada", "ocupada"]:
        return jsonify({"detail": "Estado no válido"}), 400
        
    db = next(get_db())
    try:
        table = db.query(Table).filter(Table.id == table_id).first()
        if not table:
            return jsonify({"detail": "Mesa no encontrada"}), 404
            
        table.status = nuevo_status
        db.commit()
        return jsonify({"message": f"Mesa {table.number} actualizada a {nuevo_status}"}), 200
    finally:
        db.close()

# --- LIBERAR MESA (PATCH - Admin y Mesero) ---
@table_bp.route("/<int:table_id>/release", methods=["PATCH"])
def release_table(table_id):
    current_user = get_current_user()
    if current_user.role not in ["admin", "mesero"]:
        return jsonify({"detail": "No tienes permisos"}), 403
    
    db = next(get_db())
    try:
        table = db.query(Table).filter(Table.id == table_id).first()
        if not table:
            return jsonify({"detail": "Mesa no encontrada"}), 404
        
        table.status = "libre"
        db.commit()
        return jsonify({"message": f"Mesa {table.number} liberada correctamente"}), 200
    finally:
        db.close()

# --- ELIMINAR MESA (DELETE - Solo Admin) ---
@table_bp.route("/<int:table_id>", methods=["DELETE"])
def delete_table(table_id):
    current_user = get_current_user()
    if current_user.role != "admin":
        return jsonify({"detail": "Solo el administrador puede eliminar mesas"}), 403
    
    db = next(get_db())
    try:
        table_query = db.query(Table).filter(Table.id == table_id)
        if not table_query.first():
            return jsonify({"detail": "Mesa no encontrada"}), 404
        
        table_query.delete(synchronize_session=False)
        db.commit()
        return '', 204
    finally:
        db.close()