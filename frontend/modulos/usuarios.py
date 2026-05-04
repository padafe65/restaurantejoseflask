
import streamlit as st
import requests
import pandas as pd
import time as python_time

def usuarios(API_URL, headers, rol):

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
