import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from modulos.gestion_reservas import render_reservas
import time as python_time
# Importación del nuevo módulo de componentes para el carrusel
from modulos.componentes import render_carrusel 
from modulos.informacion import render_info_institucional
from modulos.login import login
from modulos.mesas import mesas
from modulos.clientes import clientes
from modulos.usuarios import usuarios

# --- CONFIGURACIÓN INICIAL ---
LOGO_PATH = os.path.join("imagenes", "logo_restaurante.jpg")
API_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="Restaurante Don José - Gestión", layout="wide", page_icon="🍽️")

# --- 1. INICIALIZACIÓN DEL ESTADO ---
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# VARIABLES DE RESET (Cruciales para los botones cancelar)
if "reset_cliente_select" not in st.session_state:
    st.session_state.reset_cliente_select = 0
if "reset_usuario_select" not in st.session_state:
    st.session_state.reset_usuario_select = 0
if "reset_reserva_select" not in st.session_state:
    st.session_state.reset_reserva_select = 0

# --- 2. CONTROL DE NAVEGACIÓN ---
if st.session_state.token is not None:
    with st.sidebar:
        if st.button("⚠️ Recordatorio: Cierre Sesión antes de salir", width='stretch'):
            st.warning("Use el botón 'Cerrar Sesión' al final de la barra lateral.")
        if st.button("🔄 Actualizar Información", width='stretch'):
            st.rerun()
        # if st.button(f"👋 Saludar a {st.session_state.user_name}", width='stretch'):
        #     st.info(f"¡Hola, {st.session_state.user_name}! Gracias por usar el sistema de gestión del Restaurante Don José. Si necesitas ayuda, contacta al administrador.")

def pie_de_pagina():
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray; font-weight: bold; font-size: 16px;'>"
        "© 2026 Restaurante Don José - Sistema de Gestión Interna.</div>", 
        unsafe_allow_html=True
    )

# ==========================================
#                 PANTALLA DE LOGIN
# ==========================================
if st.session_state.token is None:
    
    # Esto crea la barra que al abrirla muestra las pestañas y tarjetas
    with st.expander("📌 Ver Información Institucional", expanded=False):
        render_info_institucional()
    
    render_carrusel()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("---", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH):
            _, _, col_img_center, _, _ = st.columns([1, 1, 2, 1, 1])
            with col_img_center:
                st.image(LOGO_PATH, width=180)
        st.title("🔐 Acceso al Sistema", text_alignment="center")
        
        with st.form("login_form"):
            u = st.text_input("Correo electrónico", placeholder="ejemplo@correo.com")
            p = st.text_input("Contraseña", type="password")
            login(u, p)
        pie_de_pagina()
    st.stop() 

# ==========================================
#          DASHBOARD PRINCIPAL
# ==========================================
headers = {"Authorization": f"Bearer {st.session_state.token}"}
rol = st.session_state.role

with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=150)
    st.write(f"### 👋 Hola, {st.session_state.user_name}")
    st.caption(f"Rol: {str(rol).upper()}")
    st.divider()
    if st.button("🚪 Cerrar Sesión", width='stretch', type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if rol == "admin":
    menu = ["🪑 Mesas", "👥 Clientes", "📅 Reservas", "📋 Auditoría", "⚙️ Usuarios"]
elif rol == "mesero":
    menu = ["🪑 Mesas", "👥 Clientes", "📅 Reservas"]
else:
    menu = ["🔍 Mis Reservas", "👤 Mi Perfil"]

tabs = st.tabs(menu)

# --- PESTAÑA 0: MESAS ---
with tabs[0]:
    mesas(API_URL, headers, rol)

# --- PESTAÑA 1: CLIENTES ---
with tabs[1]:
    clientes(API_URL, headers, rol)

# --- PESTAÑAS EXCLUSIVAS PARA STAFF ---
if len(tabs) > 2:
    with tabs[2]:
        render_reservas(API_URL, headers, rol)

if len(tabs) > 3 and rol == "admin":
    with tabs[3]:
        st.header("📋 Auditoría")
        if st.button("🔄 Consultar Logs"):
            res_l = requests.get(f"{API_URL}/reservations/logs", headers=headers)
            if res_l.status_code == 200:
                st.dataframe(pd.DataFrame(res_l.json()), width='stretch')

# --- PESTAÑA 4: USUARIOS ---
if len(tabs) > 4 and rol == "admin":
    with tabs[4]:
        usuarios(API_URL, headers, rol)

pie_de_pagina()