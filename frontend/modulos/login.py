import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, time as dt_time
import time as python_time
import os

# --- CONFIGURACIÓN INICIAL ---
API_URL = "http://127.0.0.1:5000"

def login(u, p):
    if st.form_submit_button("Entrar", width='stretch'):
        try:
            res = requests.post(f"{API_URL}/users/login", json={"username": u, "password": p}, timeout=5)
            if res.status_code == 200:
                d = res.json()
                st.session_state.token = d["access_token"]
                st.session_state.role = d["role"]
                st.session_state.user_id = d.get("user_id") 
                st.session_state.user_name = u.split('@')[0]
                st.success("✅ ¡Bienvenido!")
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas.")
        except requests.exceptions.ConnectionError:
                st.error("📡 Error: No se puede conectar al servidor.")
        except Exception as e:
                st.error(f"📡 Error inesperado: {str(e)}")
        st.rerun()