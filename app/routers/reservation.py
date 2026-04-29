from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.reservation import Reservation, AuditLog
from app.models.table import Table
from app.models.user import User # Asegúrate de tenerlo importado para las relaciones
from app.auth import get_current_user
from datetime import datetime

reservation_bp = Blueprint('reservation', __name__)

# --- CREAR RESERVA ---
@reservation_bp.route("/", methods=["POST"])
def create_reservation():
    current_user = get_current_user()
    if not current_user:
        return jsonify({"detail": "Token inválido o expirado"}), 401
        
    if current_user.role == "cliente":
        return jsonify({"detail": "Los clientes solo pueden consultar reservas."}), 403

    data = request.json
    db = next(get_db())
    
    try:
        # 1. Validar mesa
        table = db.query(Table).filter(Table.id == data.get('table_id')).first()
        if not table or table.status == "ocupada":
            return jsonify({"detail": "Mesa no disponible"}), 400

        # 2. Crear reserva
        new_res = Reservation(
            customer_id=data.get('customer_id'),
            table_id=data.get('table_id'),
            reservation_date=data.get('reservation_date'),
            reservation_time=data.get('reservation_time'),
            pax=data.get('pax'),
            status=data.get('status', 'confirmada'),
            created_by_user_id=current_user.id
        )
        db.add(new_res)
        db.flush() # Para obtener el ID antes del commit definitivo

        # 3. Log de Auditoría
        log = AuditLog(
            reservation_id=new_res.id,
            user_id=current_user.id,
            action="CREATE",
            details=f"Reserva creada por {current_user.role}: {current_user.username}"
        )
        db.add(log)
        
        # 4. Actualizar estado de mesa
        table.status = "reservada"
        db.commit()
        
        return jsonify({"id": new_res.id, "status": "confirmada"}), 201
    except Exception as e:
        db.rollback()
        print(f"Error al crear reserva: {e}")
        return jsonify({"detail": "Error interno al procesar la reserva"}), 500
    finally:
        db.close()

# --- LISTAR RESERVAS ---
@reservation_bp.route("/", methods=["GET"])
def get_reservations():
    current_user = get_current_user()
    if not current_user:
        return jsonify({"detail": "No autorizado"}), 401
        
    db = next(get_db())
    try:
        query = db.query(Reservation)
        
        if current_user.role == "cliente":
            # Nota: Asegúrate de que la relación 'profile' esté definida en tu modelo User
            if hasattr(current_user, 'profile') and current_user.profile:
                reservations = query.filter(Reservation.customer_id == current_user.profile.id).all()
            else:
                return jsonify([]), 200
        else:
            reservations = query.all()

        return jsonify([{
            "id": r.id,
            "customer_id": r.customer_id,
            "table_id": r.table_id,
            "num_mesa_real": r.table.number if r.table else r.table_id, # <--- AGREGAMOS ESTO
            "reservation_date": str(r.reservation_date),
            "reservation_time": str(r.reservation_time),
            "status": r.status,
            "pax": r.pax
        } for r in reservations]), 200
    finally:
        db.close()

# --- AUDITORÍA (SOLO ADMIN) ---
@reservation_bp.route("/logs", methods=["GET"])
def get_audit_logs():
    current_user = get_current_user()
    if not current_user or current_user.role != "admin":
        return jsonify({"detail": "Acceso denegado"}), 403
    
    db = next(get_db())
    try:
        logs = db.query(AuditLog).all()
        return jsonify([{
            "id": l.id,
            "res_id": l.reservation_id,
            "accion": l.action,
            "detalle": l.details,
            "fecha": l.change_date.strftime("%Y-%m-%d %H:%M:%S")
        } for l in logs]), 200
    finally:
        db.close()

# --- ACTUALIZAR ---
# --- ACTUALIZAR ---
@reservation_bp.route("/<int:res_id>", methods=["PUT"])
def update_reservation(res_id):
    current_user = get_current_user()
    if not current_user or current_user.role == "cliente":
        return jsonify({"detail": "No tienes permisos"}), 403

    db = next(get_db())
    try:
        res_query = db.query(Reservation).filter(Reservation.id == res_id)
        res = res_query.first()
        
        if not res:
            return jsonify({"detail": "Reserva no encontrada"}), 404
        
        data = request.json
        print(f"Datos recibidos para actualizar reserva {res_id}: {data}")

        # Limpiamos los datos para evitar enviar campos vacíos que den error en Postgres
        update_data = {k: v for k, v in data.items() if v is not None and v != ""}
        
        if update_data:
            res_query.update(update_data, synchronize_session=False)
        
        # Intentamos crear el Log, pero con cuidado
        try:
            log = AuditLog(
                reservation_id=res.id, 
                user_id=current_user.id, 
                action="UPDATE", 
                details=f"Reserva {res_id} modificada a estado: {data.get('status', 'N/A')} por {current_user.username}"
            )
            db.add(log)
        except Exception as log_error:
            print(f"Aviso: No se pudo crear el log de auditoría: {log_error}")
            # No bloqueamos la actualización si solo falla el log

        db.commit()
        print(f"✅ Reserva {res_id} actualizada exitosamente.")
        return jsonify({"mensaje": "Reserva actualizada"}), 200

    except Exception as e:
        db.rollback()
        print(f"❌ ERROR CRÍTICO al actualizar reserva: {str(e)}")
        return jsonify({"detail": f"Error interno: {str(e)}"}), 500
    finally:
        db.close()
# --- ELIMINAR (SOLO ADMIN) ---
@reservation_bp.route("/<int:res_id>", methods=["DELETE"])
def cancel_reservation(res_id):
    current_user = get_current_user()
    if not current_user or current_user.role != "admin":
        return jsonify({"detail": "Solo el administrador jefe puede eliminar registros"}), 403
    
    db = next(get_db())
    try:
        res_query = db.query(Reservation).filter(Reservation.id == res_id)
        if not res_query.first():
            return jsonify({"detail": "Reserva no encontrada"}), 404

        res_query.delete()
        db.commit()
        return '', 204
    except Exception as e:
        db.rollback()
        return jsonify({"detail": str(e)}), 500
    finally:
        db.close()