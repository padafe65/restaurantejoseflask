import streamlit as st
import requests
import pandas as pd
import time as python_time


def clientes(API_URL, headers, rol):
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