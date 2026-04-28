from datetime import datetime, timedelta
from jose import JWTError, jwt
from flask import request, jsonify
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User

SECRET_KEY = "tu_llave_secreta_matematica" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user():
    """
    Función para obtener el usuario desde el Token en Flask.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None 

    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    
    # Abrimos la sesión con protección total
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        return user
    except Exception as e:
        print(f"Error en get_current_user: {e}")
        return None
    finally:
        db.close()  # Se cierra pase lo que pase