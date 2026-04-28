import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from modulos.gestion_reservas import render_reservas
import time as python_time 

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
if "reset_u" not in st.session_state: 
    st.session_state.reset_u = 0

# --- 2. CONTROL DE NAVEGACIÓN ---
if st.session_state.token is not None:
    with st.sidebar:
        if st.button("⚠️ Recordatorio: Cierre Sesión antes de salir", width='stretch'):
            st.warning("Use el botón 'Cerrar Sesión' al final de la barra lateral.")

def pie_de_pagina():
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "© 2026 Restaurante Don José - Sistema de Gestión Interna.</div>", 
        unsafe_allow_html=True
    )

# ==========================================
#                 PANTALLA DE LOGIN
# ==========================================
if st.session_state.token is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=200)
        st.title("🔐 Acceso al Sistema")
        
        with st.form("login_form"):
            u = st.text_input("Correo electrónico", placeholder="ejemplo@correo.com")
            p = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Entrar"):
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
                    st.error("📡 Error: No se puede conectar al servidor. ¿Flask está corriendo en localhost:5000?")
                except requests.exceptions.Timeout:
                    st.error("📡 Error: Tiempo de espera agotado. El servidor tardó demasiado en responder.")
                except Exception as e:
                    st.error(f"📡 Error inesperado: {str(e)}")
        pie_de_pagina()
    st.stop() 

# ==========================================
#          DASHBOARD PRINCIPAL
# ==========================================
headers = {"Authorization": f"Bearer {st.session_state.token}"}
rol = st.session_state.role

# --- BARRA LATERAL ---
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

# --- DEFINICIÓN DE MENÚ SEGÚN ROL ---
if rol == "admin":
    menu = ["🪑 Mesas", "👥 Clientes", "📅 Reservas", "📋 Auditoría", "⚙️ Usuarios"]
elif rol == "mesero":
    menu = ["🪑 Mesas", "👥 Clientes", "📅 Reservas"]
else:
    menu = ["🔍 Mis Reservas", "👤 Mi Perfil"]

tabs = st.tabs(menu)

# --- PESTAÑA 0: MESAS (STAFF) o MIS RESERVAS (CLIENTE) ---
# --- PESTAÑA 0: MESAS (STAFF) o MIS RESERVAS (CLIENTE) ---
with tabs[0]:
    if rol in ["admin", "mesero"]:
        st.header("🪑 Estado de las Mesas")
        
        res_t = requests.get(f"{API_URL}/tables/", headers=headers)
        res_r_check = requests.get(f"{API_URL}/reservations/", headers=headers)
        
        if res_t.status_code == 200:
            mesas_list = res_t.json()
            reservas_raw = res_r_check.json() if res_r_check.status_code == 200 else []
            
            # --- BLOQUE DE COHERENCIA Y CONTEO ---
            for m in mesas_list:
                # 1. Sincronización de estados (tu lógica actual)
                tiene_reserva = any(r['table_id'] == m['id'] and r['status'] == 'confirmada' for r in reservas_raw)
                if tiene_reserva and m['status'] == 'libre':
                    requests.put(f"{API_URL}/tables/{m['id']}", json={"status": "reservada"}, headers=headers)
                    m['status'] = 'reservada'
                elif not tiene_reserva and m['status'] == 'reservada':
                    requests.patch(f"{API_URL}/tables/{m['id']}/release", headers=headers)
                    m['status'] = 'libre'
                
                # 2. NUEVA LÓGICA: Conteo de estados por mesa
                m['Confirmadas'] = sum(1 for r in reservas_raw if r['table_id'] == m['id'] and r['status'] == 'confirmada')
                m['Canceladas'] = sum(1 for r in reservas_raw if r['table_id'] == m['id'] and r['status'] == 'cancelada')
                m['Finalizadas'] = sum(1 for r in reservas_raw if r['table_id'] == m['id'] and r['status'] == 'finalizada')

            # --- MÉTRICAS VISUALES (Se mantienen igual) ---
            cols = st.columns(4) 
            for i, mesa in enumerate(mesas_list):
                with cols[i % 4]:
                    emoji = "🔴" if mesa['status'] == 'ocupada' else "🟡" if mesa['status'] == 'reservada' else "🟢"
                    st.metric(label=f"Mesa {mesa['number']}", value=mesa['status'].upper(), delta=emoji)
                    
                    if mesa['status'] in ['ocupada', 'reservada']:
                        if st.button(f"🔓 Liberar #{mesa['number']}", key=f"btn_lib_{mesa['id']}"):
                            if mesa['Confirmadas'] > 0:
                                st.error(f"Acción bloqueada: Hay reserva activa.")
                            else:
                                r = requests.patch(f"{API_URL}/tables/{mesa['id']}/release", headers=headers)
                                if r.status_code == 200:
                                    st.toast(f"Mesa {mesa['number']} LIBRE")
                                    python_time.sleep(0.5)
                                    st.rerun()

            st.divider()
            st.subheader("📋 Listado Detallado de Mesas")
            df_mesas = pd.DataFrame(mesas_list)
            if not df_mesas.empty:
                # Definimos las columnas que queremos mostrar, incluyendo los nuevos conteos
                columnas_mesas = {
                    'number': 'Mesa #',
                    'capacity': 'Capacidad',
                    'status': 'Estado Actual',
                    'Confirmadas': '✅ Confirmadas',
                    'Canceladas': '❌ Canceladas',
                    'Finalizadas': '🏁 Finalizadas'
                }
                st.dataframe(
                    df_mesas[list(columnas_mesas.keys())].rename(columns=columnas_mesas), 
                    use_container_width=True,
                    hide_index=True
                )
# --- PESTAÑA 1: CLIENTES ---
with tabs[1]:
    if rol in ["admin", "mesero"]:
        st.header("👥 Gestión de Clientes")
        res_c = requests.get(f"{API_URL}/customers/", headers=headers)
        if res_c.status_code == 200:
            c_list = res_c.json()
            st.dataframe(pd.DataFrame(c_list), use_container_width=True)
            st.divider()
            # MEJORA VISUAL: Nombre con ID
            opciones_c = {f"{c['full_name']} (ID: {c['id']})": c for c in c_list}
            sel_c = st.selectbox("Seleccionar Cliente para editar:", ["-- Seleccionar --"] + list(opciones_c.keys()))
            c_sel = opciones_c.get(sel_c, {"id": 0, "full_name": "", "phone": "", "whatsapp": "", "address": ""})
            
            if c_sel['id'] != 0:
                with st.form("staff_edit_customer"):
                    f_name = st.text_input("Nombre", value=c_sel['full_name'])
                    f_phone = st.text_input("Teléfono", value=c_sel['phone'])
                    f_ws = st.text_input("WhatsApp", value=c_sel['whatsapp'])
                    f_dir = st.text_input("Dirección", value=c_sel.get('address',''))
                    if st.form_submit_button("💾 Guardar cambios"):
                        payload = {"full_name": f_name, "phone": f_phone, "whatsapp": f_ws, "address": f_dir}
                        requests.put(f"{API_URL}/customers/{c_sel['id']}", json=payload, headers=headers)
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
                st.success("¡Perfil actualizado!")
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
                st.dataframe(pd.DataFrame(res_l.json()), use_container_width=True)

if len(tabs) > 4 and rol == "admin":
    with tabs[4]:
        st.header("⚙️ Gestión de Usuarios")
        res_u = requests.get(f"{API_URL}/users/", headers=headers)
        if res_u.status_code == 200:
            u_list = res_u.json()
            st.dataframe(pd.DataFrame(u_list), use_container_width=True)
            st.divider()
            op_u = {f"{u['username']}": u for u in u_list}
            sel_u = st.selectbox("Editar Usuario:", ["-- Nuevo --"] + list(op_u.keys()))
            u_dat = op_u.get(sel_u, {"id": 0, "email": "", "username": "", "role": "cliente"})
            with st.form("edit_user"):
                un = st.text_input("Username", value=u_dat['username'])
                em = st.text_input("Email", value=u_dat['email'])
                ro = st.selectbox("Rol", ["admin", "mesero", "cliente"], index=["admin", "mesero", "cliente"].index(u_dat['role']))
                if st.form_submit_button("💾 Guardar"):
                    payload = {"username": un, "email": em, "role": ro, "is_active": True}
                    if u_dat['id'] == 0:
                        payload["password"] = "123456"
                        requests.post(f"{API_URL}/users/", json=payload, headers=headers)
                    else:
                        requests.put(f"{API_URL}/users/{u_dat['id']}", json=payload, headers=headers)
                    st.rerun()

pie_de_pagina()