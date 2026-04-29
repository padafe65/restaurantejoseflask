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

# --- CONFIGURACIÓN INICIAL ---
LOGO_PATH = os.path.join("frontend", "logo_restaurante.jpg")
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
#if "reset_u" not in st.session_state: 
#    st.session_state.reset_u = 0

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
        st.markdown("<br>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=200)
        st.title("🔐 Acceso al Sistema")
        
        with st.form("login_form"):
            u = st.text_input("Correo electrónico", placeholder="ejemplo@correo.com")
            p = st.text_input("Contraseña", type="password")
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
    if rol in ["admin", "mesero"]:
        st.header("🪑 Estado de las Mesas")
        res_t = requests.get(f"{API_URL}/tables/", headers=headers)
        res_r_check = requests.get(f"{API_URL}/reservations/", headers=headers)
        
        if res_t.status_code == 200:
            mesas_list = res_t.json()
            reservas_raw = res_r_check.json() if res_r_check.status_code == 200 else []
            
            for m in mesas_list:
                tiene_reserva = any(r['table_id'] == m['id'] and r['status'] == 'confirmada' for r in reservas_raw)
                if tiene_reserva and m['status'] == 'libre':
                    requests.put(f"{API_URL}/tables/{m['id']}", json={"status": "reservada"}, headers=headers)
                    m['status'] = 'reservada'
                elif not tiene_reserva and m['status'] == 'reservada':
                    requests.patch(f"{API_URL}/tables/{m['id']}/release", headers=headers)
                    m['status'] = 'libre'
                
                m['Confirmadas'] = sum(1 for r in reservas_raw if r['table_id'] == m['id'] and r['status'] == 'confirmada')

            cols = st.columns(4) 
            for i, mesa in enumerate(mesas_list):
                with cols[i % 4]:
                    emoji = "🔴" if mesa['status'] == 'ocupada' else "🟡" if mesa['status'] == 'reservada' else "🟢"
                    st.metric(label=f"Mesa {mesa['number']}", value=mesa['status'].upper(), delta=emoji)
                    if mesa['status'] in ['ocupada', 'reservada']:
                        if st.button(f"🔓 Liberar #{mesa['number']}", key=f"btn_lib_{mesa['id']}"):
                            if mesa.get('Confirmadas', 0) > 0:
                                st.error("Acción bloqueada: Hay reserva activa.")
                            else:
                                requests.patch(f"{API_URL}/tables/{mesa['id']}/release", headers=headers)
                                st.rerun()

            st.divider()
            st.dataframe(pd.DataFrame(mesas_list), width="stretch", hide_index=True)

# --- PESTAÑA 1: CLIENTES ---
with tabs[1]:
    if rol in ["admin", "mesero"]:
        st.header("👥 Gestión de Clientes")
        res_c = requests.get(f"{API_URL}/customers/", headers=headers)
        if res_c.status_code == 200:
            c_list = res_c.json()
            st.dataframe(pd.DataFrame(c_list), width="stretch")
            st.divider()

            opciones_c = {f"{c['full_name']} (ID: {c['id']})": c for c in c_list}
            sel_c = st.selectbox(
                "Seleccionar Cliente para editar:", 
                ["-- Seleccionar --"] + list(opciones_c.keys()),
                key=f"sb_cli_{st.session_state.reset_cliente_select}" 
            )
            
            c_sel = opciones_c.get(sel_c, {"id": 0, "full_name": "", "phone": "", "whatsapp": "", "address": ""})
            
            if c_sel['id'] != 0:
                with st.form("staff_edit_customer"):
                    st.subheader(f"📝 Editando: {c_sel['full_name']}")
                    f_name = st.text_input("Nombre", value=c_sel['full_name'])
                    f_phone = st.text_input("Teléfono", value=c_sel['phone'])
                    f_ws = st.text_input("WhatsApp", value=c_sel['whatsapp'])
                    f_dir = st.text_input("Dirección", value=c_sel.get('address',''))
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.form_submit_button("💾 Guardar cambios", width="stretch"):
                            payload = {"full_name": f_name, "phone": f_phone, "whatsapp": f_ws, "address": f_dir}
                            requests.put(f"{API_URL}/customers/{c_sel['id']}", json=payload, headers=headers)
                            st.success("✅ Cambios guardados")
                            python_time.sleep(1)
                            st.rerun()
                    with c2:
                        if st.form_submit_button("❌ Cancelar", width="stretch"):
                            st.session_state.reset_cliente_select += 1
                            st.rerun()
    else:
        st.header("👤 Mi Perfil")
        res_c = requests.get(f"{API_URL}/customers/", headers=headers)
        mi_ficha = {"id": 0, "full_name": st.session_state.user_name, "phone": "", "whatsapp": "", "address": ""}
        if res_c.status_code == 200:
            mi_ficha = next((c for c in res_c.json() if c.get('user_id') == st.session_state.user_id), mi_ficha)
        with st.form("perfil_cliente_self"):
            fn = st.text_input("Nombre Completo", value=mi_ficha['full_name'])
            ph = st.text_input("Teléfono", value=mi_ficha['phone'])
            ws = st.text_input("WhatsApp", value=mi_ficha['whatsapp'])
            ad = st.text_input("Dirección", value=mi_ficha.get('address',''))
            if st.form_submit_button("💾 Actualizar"):
                payload = {"full_name": fn, "phone": ph, "whatsapp": ws, "address": ad, "user_id": st.session_state.user_id}
                if mi_ficha['id'] != 0:
                    requests.put(f"{API_URL}/customers/{mi_ficha['id']}", json=payload, headers=headers)
                else:
                    requests.post(f"{API_URL}/customers/", json=payload, headers=headers)
                st.success("✅ ¡Perfil actualizado!")
                python_time.sleep(1)
                st.rerun()

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
        st.header("⚙️ Gestión de Usuarios")
        res_u = requests.get(f"{API_URL}/users/", headers=headers)
        if res_u.status_code == 200:
            u_list = res_u.json()
            st.dataframe(pd.DataFrame(u_list), width='stretch')
            st.divider()
            
            op_u = {f"{u['username']}": u for u in u_list}
            sel_u = st.selectbox(
                "Editar Usuario:", 
                ["-- Seleccionar --", "-- Nuevo --"] + list(op_u.keys()),
                key=f"sb_user_{st.session_state.reset_usuario_select}"
            )
            
            if sel_u not in ["-- Seleccionar --"]:
                u_dat = op_u.get(sel_u, {"id": 0, "email": "", "username": "", "role": "cliente"})
                with st.form("edit_user"):
                    un = st.text_input("Username", value=u_dat['username'])
                    em = st.text_input("Email", value=u_dat['email'])
                    ro = st.selectbox("Rol", ["admin", "mesero", "cliente"], index=["admin", "mesero", "cliente"].index(u_dat['role']))
                    
                    pw, pw_confirm = None, None
                    if u_dat['id'] == 0:
                        st.markdown("### 🔐 Configurar Contraseña")
                        pw = st.text_input("Contraseña", type="password")
                        pw_confirm = st.text_input("Confirmar Contraseña", type="password")
                    
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.form_submit_button("💾 Guardar", width="stretch"):
                            if u_dat['id'] == 0:
                                if not pw or pw != pw_confirm:
                                    st.error("❌ Las contraseñas no coinciden")
                                else:
                                    payload = {"username": un, "email": em, "role": ro, "is_active": True, "password": pw}
                                    res = requests.post(f"{API_URL}/users/", json=payload, headers=headers)
                                    if res.status_code == 201:
                                        st.success("✅ Usuario creado")
                                        python_time.sleep(1); st.rerun()
                            else:
                                payload = {"username": un, "email": em, "role": ro, "is_active": True}
                                res = requests.put(f"{API_URL}/users/{u_dat['id']}", json=payload, headers=headers)
                                if res.status_code == 200:
                                    st.success("✅ Usuario actualizado")
                                    python_time.sleep(1); st.rerun()
                    with b2:
                        if st.form_submit_button("❌ Cancelar", width="stretch"):
                            st.session_state.reset_usuario_select += 1
                            st.rerun()

pie_de_pagina()